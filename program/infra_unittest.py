import unittest
import pulumi

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, type_, name, inputs, provider, id_):
        return [name + '_id', inputs]
    def call(self, token, args, provider):
        return {}

pulumi.runtime.set_mocks(MyMocks())

# It's important to import `infra` _after_ the mocks are defined.
import infra

class TestingWithMocks(unittest.TestCase):        
    # Lambdas should have a maximum timeout of 10sec.
    @pulumi.runtime.test
    def test_lambda_timeout(self):
        def check_timeout(args):
            urn, timeout = args
            print(urn)
            print(timeout)            
            self.assertIsNotNone(timeout, f'lambda {urn} must have timeout')
            self.assertGreaterEqual(timeout,10,f'lambda {urn} must have a timeout than than or equal to 10')                
        return pulumi.Output.all(infra.lambda_fn.urn, infra.lambda_fn.timeout).apply(check_timeout)

#     # # check 1: Instances have a Name tag.
#     # @pulumi.runtime.test
#     # def test_dynamodb_tags(self):
#     #     def check_name(args):
#     #         urn, billing_mode = args
#     #         print(urn)
#     #         print(args)
#     #         self.assertIsNotNone(billing_mode, f'server {urn} must have tags')
#     #         self.assertEqual('PROVISIONED', billing_mode, 'server {urn} must have a name tag')

#     #     return pulumi.Output.all(infra.dynamodb_table.urn, infra.dynamodb_table.billing_mode).apply(check_name)

#     # # check 1: Instances have a Name tag.
#     # @pulumi.runtime.test
#     # def test_server_tags(self):
#     #     def check_tags(args):
#     #         urn, tags = args
#     #         print(urn)
#     #         print(tags)
#     #         print(args)
#     #         self.assertIsNotNone(tags, f'server {urn} must have tags')
#     #         self.assertIn('Name', tags, 'server {urn} must have a name tag')

#     #     return pulumi.Output.all(infra.server.urn, infra.server.tags).apply(check_tags)

#     # # check 2: Instances must not use an inline userData script.
#     # @pulumi.runtime.test
#     # def test_server_userdata(self):
#     #     def check_user_data(args):
#     #         urn, user_data = args
#     #         self.assertFalse(user_data, f'illegal use of user_data on server {urn}')

#     #     return pulumi.Output.all(infra.server.urn, infra.server.user_data).apply(check_user_data)    

#     # # check 3: Test if port 22 for ssh is exposed.
#     # @pulumi.runtime.test
#     # def test_security_group_rules(self):
#     #     def check_security_group_rules(args):
#     #         urn, ingress = args
#     #         ssh_open = any([rule['from_port'] == 22 and any([block == "0.0.0.0/0" for block in rule['cidr_blocks']]) for rule in ingress])
#     #         self.assertFalse(ssh_open, f'security group {urn} exposes port 22 to the Internet (CIDR 0.0.0.0/0)')

#     #     return pulumi.Output.all(infra.group.urn, infra.group.ingress).apply(check_security_group_rules)    

#     # # check 1: Lambdas should have a minimum timeout of 30sec.
#     # @pulumi.runtime.test
#     # def test_lambda_timeout(self):
#     #     def check_timeout(args):
#     #         urn, timeout = args
#     #         self.assertIsNotNone(timeout, f'lambda {urn} must have timeout')
#     #         self.assertGreaterEqual(timeout,30,f'lambda {urn} must have a timeout greater or equal to 30')
#     #     return pulumi.Output.all(infra.lambda_fn.urn, infra.lambda_fn.timeout).apply(check_timeout)

#     # # check 2: Bucket to have 'bucket' parameter.
#     # @pulumi.runtime.test
#     # def test_bucket_name(self):
#     #     def check_name(args):
#     #         urn, bucket = args
#     #         self.assertIsNotNone(bucket, f'Bucket {urn} must have a bucket parameter with a name')
#     #     return pulumi.Output.all(infra.serverless_webapp_bucket_name.urn, infra.serverless_webapp_bucket_name.bucket).apply(check_name)    


#     # # check 3: DynamoDB table should have stream_view_type as NEW_IMAGE
#     # @pulumi.runtime.test
#     # def test_dynamodb_stream_type(self):
#     #     def check_stream_view(args):
#     #         urn, stream_view_type = args
#     #         self.assertIsNotNone(stream_view_type, f'Table {urn} should have stream_view_type parameter')
#     #         self.assertEqual('NEW_IMAGE',stream_view_type,f'Table should have NEW_IMAGE as stream view type value')
#     #     return pulumi.Output.all(infra.dynamodb_table.urn, infra.dynamodb_table.stream_view_type).apply(check_stream_view)
