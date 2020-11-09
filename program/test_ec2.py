import unittest
import pulumi

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, type_, name, inputs, provider, id_):
        return [name + '_id', inputs]
    def call(self, token, args, provider):
        return {}

# ... MyMocks as shown above
pulumi.runtime.set_mocks(MyMocks())

# It's important to import `infra` _after_ the mocks are defined.
import infra

class TestingWithMocks(unittest.TestCase):
    # check 1: Instances have a Name tag.
    # @pulumi.runtime.test
    def test_server_tags(self):
        try:    
            print("Test")
        except ValueError as e:
            print(e)