from app.cache.redis import redis_client
from app.utils.exceptions import SourceUnavailableError
from app.utils.logger import get_logger

logger = get_logger("circuit_breaker")

class CircuitBreaker:
    CHECK_SCRIPT = """
    local state = redis.call('get', KEYS[1])
    local needs_ho = redis.call('get', KEYS[2])
    
    if state == 'OPEN' then
        return 'OPEN'
    elseif not state and needs_ho == '1' then
        redis.call('set', KEYS[1], 'HALF_OPEN', 'EX', 15)
        redis.call('del', KEYS[2])
        return 'HALF_OPEN_READY'
    elseif state == 'HALF_OPEN' then
        return 'HALF_OPEN_TESTING'
    else
        return 'CLOSED'
    end
    """

    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.key_prefix = f"cb:{self.name}"
        
        self.state_key = f"{self.key_prefix}:state"
        self.needs_ho_key = f"{self.key_prefix}:needs_ho"
        self.fails_key = f"{self.key_prefix}:fails"
        self.test_lock_key = f"{self.key_prefix}:test_lock"

    async def check_state(self):
        result = await redis_client.client.eval(self.CHECK_SCRIPT, 2, self.state_key, self.needs_ho_key)
        
        if result == 'OPEN':
            raise SourceUnavailableError("Source is blocked (Circuit OPEN).")
        elif result == 'HALF_OPEN_TESTING':
            raise SourceUnavailableError("Circuit is HALF_OPEN. Awaiting test result.")

    async def record_failure(self):
        state = await redis_client.client.get(self.state_key)
        
        if state == "HALF_OPEN":
            logger.error(f"Circuit {self.name} test FAILED. Re-opening for {self.recovery_timeout}s.")
            await redis_client.client.delete(self.test_lock_key)
            await self._trip_circuit()
        else:
            fails = await redis_client.client.incr(self.fails_key)
            if fails == 1:
                await redis_client.client.expire(self.fails_key, self.recovery_timeout)
            if fails >= self.failure_threshold:
                logger.error(f"Circuit {self.name} TRIPPED! Opening for {self.recovery_timeout}s.")
                await self._trip_circuit()

    async def record_success(self):
        state = await redis_client.client.get(self.state_key)
        if state == "HALF_OPEN":
            logger.info(f"Circuit {self.name} test SUCCEEDED. Closing circuit.")
            await redis_client.client.delete(self.state_key)
            await redis_client.client.delete(self.test_lock_key)
        
        await redis_client.client.delete(self.fails_key)

    async def _trip_circuit(self):
        await redis_client.client.setex(self.state_key, self.recovery_timeout, "OPEN")
        await redis_client.client.set(self.needs_ho_key, "1")