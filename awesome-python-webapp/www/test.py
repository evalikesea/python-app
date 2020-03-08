import orm, asyncio, sys
from models import User

async def test(loop):
    await orm.create_pool(loop=loop, user='www-data', password='www-data',db='awesome')
    u= User(name='Test', email='test3@example.com',passwd='12345678',image='about:blank')
    # await u.save()
def count():
    def f(j):
        def g():
            return j * j

        return g

    fs = []
    for i in range(1, 4):
        fs.append(f(i))  # f(i)立刻被执行，因此i的当前值被传入f()
    print(fs)
    return fs

f1, f2, f3 = count()
if __name__ =='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(loop))
    # loop.close()
    if loop.is_closed():
        sys.exit(0)
    f1,f2,f3 = count()
    print(f1())
    print(f2())
    print(f3())
