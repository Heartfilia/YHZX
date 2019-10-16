class Test(object):
    def __init__(self):
        print('init')

    def you(self):
        print('you')


def mian():
    t = Test()
    t.you()


if __name__ == '__main__':
    print('name')
    mian()
    print('main')
