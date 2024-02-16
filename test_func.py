a = 3
b = 4

json = {
    'a': 5,
    'b': 6
}
# print(type(json))


def fun(a=1, b=2, **kwargs):
    # **kwargs):
    # print(kwargs)
    # if "a" in kwargs:
    #     print(f"a key in {kwargs}")
    # json = {
    #     'a': a,
    #     'b': b
    # }
    # print(json)
    print(**kwargs)


# fun(**json)
#**json)

foo = {'name': 'Bogdan', 'posts_qty': 25, 'biz': 'bar', 'baz': 'foo'}
# foo = {'biz': 'bar', 'foo': 'fob'}

# foo = {'foo': 'bar'}

def get_posts_info(name='foo', posts_qty=30, **kwargs):
# def get_posts_info(**kwargs):
    print(name, posts_qty, kwargs)
    # for k, v in kwargs.items():
    #     print(k,v)
        # print(kwargs)


get_posts_info(**foo)
