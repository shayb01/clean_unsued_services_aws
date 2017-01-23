def worker(credentials):

    import boto.ec2.autoscale
    import exceptions

    asg_conn = boto.ec2.autoscale.connect_to_region(credentials["region"], aws_access_key_id=credentials["private_key"], aws_secret_access_key=credentials["secret_key"])

    def get_all_asg_and_linked_lcg():
        result = []
        asg_list = asg_conn.get_all_groups()

        if asg_list:
            for asg in asg_list:
                lcg = asg_conn.get_all_launch_configurations(names=[asg.launch_config_name], max_records=1)[0]
                result.append({'asg': asg, 'lcg': lcg})

        return result

    def clean_unused_lcg(lcg_list):
        result = []
        existing_lcg_list = asg_conn.get_all_launch_configurations()
        for lcg in existing_lcg_list:
            if lcg.name not in lcg_list:
                try:
                    logMSG = ('Trying to delete LCG: %s' % lcg.name)
                    asg_conn.delete_launch_configuration(lcg.name)
                    result.append(lcg.name)
                except Exception as e:
                    if isinstance(e, boto.exception.BotoServerError):
                        if e.error_code == 'ResourceInUse':
                            pass
                        else:
                            print e.message
                    elif isinstance(e, exceptions.IndexError):
                        print e.message
                        pass
                    else:
                        print str(e)
        if len(result) == 0:
            result.append('No LCG to delete')

        return result

    return {"answer": clean_unused_lcg(get_all_asg_and_linked_lcg())}


