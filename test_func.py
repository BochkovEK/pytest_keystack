
foo = {'name': 'Bogdan', 'posts_qty': 25, 'biz': 'bar', 'baz': 'foo'}
# foo = {'biz': 'bar', 'foo': 'fob'}



def get_posts_info(
        name='foo',
        posts_qty=30,
        **kwargs):
    # kwargs['name'] = 'bazz'
    server_create_prop = {
        'name': name,
        'posts_qty': posts_qty,
        **kwargs
    }
    print(server_create_prop)

foo['name'] = 'foo-1'
get_posts_info(**foo)
foo['name'] = 'foo-2'
get_posts_info(**foo)
