from tori.session.repository.base   import Base   as BaseSessionAdapter
from tori.session.repository.file   import File   as FileSessionAdapter
from tori.session.repository.memory import Memory as InMemorySessionAdapter
from tori.session.repository.xredis import Redis  as RedisSessionAdapter