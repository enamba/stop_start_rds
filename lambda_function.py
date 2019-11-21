import boto3
import time
from datetime import tzinfo, timedelta, datetime
import os
import re


def lambda_handler(event, context):
    time.tzset()
    hour = time.strftime('%H')

    rds = boto3.client('rds', region_name=os.environ['REGION_NAME'])
    dbs = rds.describe_db_instances()
    turnOff_instancesId = []
    turnOn_instancesId = []
    weekArray = ["[0-1]", "[0-1]", "[0-1]", "[0-1]", "[0-1]", "[0-1]", "[0-1]"]
    weekArray[int(time.strftime('%w'))] = "[1]"
    findWeek = '.'.join(weekArray)
    print('Hour: ' + str(hour))
    print('findWeek: ' + findWeek)

    actions = []

    for db in dbs['DBInstances']:
        db_tags = rds.list_tags_for_resource(ResourceName=db['DBInstanceArn'])
        itens_search = 0
        action = {}
        action[db['DBInstanceIdentifier']] = {}
        tags_filtered = {}
        for tag in db_tags['TagList']:
            if tag['Key'] == 'off':
                tags_filtered['off'] = tag['Value']
                itens_search = itens_search + 1
            if tag['Key'] == 'on':
                tags_filtered['on'] = tag['Value']
                itens_search = itens_search + 1
            if tag['Key'] == 'weekday_on':
                itens_search = itens_search + 1
                if re.match(findWeek, tag['Value']) is not None:
                    print('Essa ARN deve executar hoje: '
                          + db['DBInstanceIdentifier'])
                else:
                    itens_search = 0

        if itens_search == 3:
            action[db['DBInstanceIdentifier']] = tags_filtered
            actions.append(action)

    print('actions: ' + str(actions))
    for action in actions:
        key = action.keys()
        key = list(key)[0]
        if action[key]['on'] != action[key]['off']:
            if action[key]['on'] == hour:
                try:
                    rds.start_db_instance(DBInstanceIdentifier=key)
                    print('Ligando: ' + key)
                except:
                    print('Ja ligado: ' + key)
            if action[key]['off'] == hour:
                try:
                    rds.stop_db_instance(DBInstanceIdentifier=key)
                    print('Desligando: ' + key)
                except:
                    print('Ja desligado: ' + key)
        else:
            print('Horario de ligar e desligar eh o mesmo: ' + key)


if __name__ == '__main__':
    lambda_handler('', '')
