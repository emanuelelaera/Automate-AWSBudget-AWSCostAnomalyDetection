# Author: Emanuele Laera

from turtle import done
from pickletools import float8
import boto3
import collections
import os
import subprocess
import botocore
from string import Template
class CustomTemplate(Template):
	delimiter = '§'

### VARIABLES
support_mail = '' #Insert Support Mail

new_budget_name = ""
new_monitor_name = ""
aws_budget_forecasted = 95
aws_budget_actual = 100

cyan = '\u001b[96m'
blue = '\u001b[94m'
green = '\u001b[92m'
red = '\u001b[31m'
CEND = '\033[0m'

menu = {
    1: 'Budget Alarm (AWS Budget)',
    2: 'Cost Anomaly Detection (AWS Cost Explorer)',
    3: 'Both of them',
    4: 'Exit',
}

budget_anomaly_menu = {
    1: 'Alarm on the total budget of the Organization and Anomaly Monitor on all services',
    2: 'Alarm on the Budget and Anomaly Monitor of a single Organization account',
    3: 'Alarm on the Budget and Anomaly Monitor of all accounts related to an Organizational Unit',
    4: 'Return',
}

budget_alarm_menu = {
    1: "Alarm on the total budget of the Organization",
    2: "Alarm on the budget of a single account of the Organization",
    3: "Alarm on the budget of all accounts related to an Organizational Unit",
    4: 'Return',
}

anomaly_detection_menu = {
    1: "Anomaly Detection Monitor on all the Organization's services",
    2: "Anomaly Detection Monitor on a single Organization account",
    3: "Anomaly Detection Monitor on all accounts related to an Organizational Unit",
    4: 'Return',
}

mail_no_yes = {
    1: 'NO',
    2: 'YES',
}

### FUNCTIONS
def print_menu():
    for key in menu.keys():
        print (key, '--', menu[key] )
   
def print_budget_anomaly_menu():
    for key in budget_anomaly_menu.keys():
        print (key, '--', budget_anomaly_menu[key] )   
        
def print_budget_alarm_menu():
    for key in budget_alarm_menu.keys():
        print (key, '--', budget_alarm_menu[key] )

def print_anomaly_detection_menu():
    for key in anomaly_detection_menu.keys():
        print (key, '--', anomaly_detection_menu[key] )
        
def print_mail_no_yes():
    for key in mail_no_yes.keys():
        print (key, '--', mail_no_yes[key] )        

def check_budget_anomaly_name(session, account_id):
    check_budget = session.client('budgets')
    DescribeBudget = check_budget.describe_budgets(AccountId=account_id)
    print(green + "\nNow you need to choose a name for the alarm." + CEND)
    try:
        budget_names = [budget_name["BudgetName"] for budget_name in DescribeBudget["Budgets"]]
        if len(budget_names) == 0:
            print(blue + "\nAt the moment there are no other alarms on the Budget." + CEND) 
        else:
            print(blue + "\nAt the moment, the existing names are:\n" + CEND)
            for item in budget_names:
                print(item)
    except:
        print(blue + "\nAt the moment there are no other alarms on the Budget." + CEND) 
    print(green + "\nEnter the name you want to give the alarm on the Budget.\n" + CEND)
    global new_budget_name
    new_budget_name=input()
    try:
        equal_elements=collections.Counter(budget_names)[new_budget_name]
    except:
        equal_elements=0
    while equal_elements !=0:
        print(red + "\nThere is already a Budget alert in the AWS Budget service of the account in question with this name." + CEND)
        print(red + "\nTry again, enter a different name:\n"+ CEND)
        new_budget_name=input()
        equal_elements=collections.Counter(budget_names)[new_budget_name]
    
    os.system("clear")    
    anomaly_detection = session.client('ce')
    describe_anomaly_monitors = anomaly_detection.get_anomaly_monitors()
    print(green + "\nNow you need to choose a name for the monitor." + CEND)
    try:
        monitor_names = [monitor_name["MonitorName"] for monitor_name in describe_anomaly_monitors["AnomalyMonitors"]]
        if len(monitor_names) == 0:
            print(blue + "\nThere are currently no other Anomaly Detection Monitors." + CEND) 
        else:
            print(blue + "\nAt the moment, the existing names are:\n" + CEND)
            for item in monitor_names:
                print(item)
    except:
        print(blue + "\nThere are currently no other Anomaly Detection Monitors." + CEND)     
    print(green + "\nEnter the name you want to give to the Anomaly Detection Monitor.\n" + CEND)
    global new_monitor_name   
    new_monitor_name=input()
    try:
        equal_elements=collections.Counter(monitor_names)[new_monitor_name]
    except:
        equal_elements=0   
    while equal_elements !=0:
        print(red + "\nA monitor with this name already exists." + CEND)
        print(red + "\nTry again, enter a different name:\n"+ CEND)
        new_monitor_name=input()
        equal_elements=collections.Counter(monitor_names)[new_monitor_name]

def new_subscriber_budget_anomaly_full(new_budget_name, new_monitor_name, budget, anomaly_detection_threshold, session):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added correctly!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''- SubscriptionType: EMAIL
              Address: ''' + i + '''
            '''
                new_mails+= mail

            new_mails_1 = ''''''
            for i in mails:
                mail_1='''{
                "Type": "EMAIL",
                "Address": ''' + '"' + i + '"' + '''
                },
            '''
                new_mails_1+= mail_1
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget and Cost Anomaly Detection: Enable AWS Budget and Cost Anomaly Detection"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
            
  CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: §ANOMALY_DETECTION_NAME
            MonitorType: 'DIMENSIONAL'
            MonitorDimension: 'SERVICE' 

  CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: §ANOMALY_SUBSCRIPTION_MAME
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                },
                §MAILS
            ]'''
            an_bdg = CustomTemplate(b)
            budget_anomaly_template = (an_bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = "'" + new_monitor_name + "'", ANOMALY_SUBSCRIPTION_MAME = '"' + new_monitor_name + '-Subscription"', NEW_MAILS=new_mails, MAILS =new_mails_1 ))
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Monitoring-"+new_budget_name+"--"+new_monitor_name,
            TemplateBody=budget_anomaly_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added correctly!" + CEND)
            mails.append(new_mail_2)

def new_subscriber_budget_anomaly_selective(new_budget_name, new_monitor_name, budget, anomaly_detection_threshold, session, specific_account):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added correctly!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''- SubscriptionType: EMAIL
              Address: ''' + i + '''
            '''
                new_mails+= mail

            new_mails_1 = ''''''
            for i in mails:
                mail_1='''{
                "Type": "EMAIL",
                "Address": ''' + '"' + i + '"' + '''
                },
            '''
                new_mails_1+= mail_1
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget and Cost Anomaly Detection: Enable AWS Budget and Cost Anomaly Detection"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters: 
          LinkedAccount:
            - §SPECIFIC_ACCOUNT
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
            
  CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ "§SPECIFIC_ACCOUNT" ]
                    }
                }'

  CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                },
                §MAILS
            ]'''
            an_bdg = CustomTemplate(b)
            budget_anomaly_template = (an_bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', NEW_MAILS=new_mails, MAILS =new_mails_1, SPECIFIC_ACCOUNT = specific_account))
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Monitoring-"+new_budget_name+"--"+new_monitor_name,
            TemplateBody=budget_anomaly_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)

def new_subscriber_budget_anomaly_ou(new_budget_name, new_monitor_name, budget, anomaly_detection_threshold, session, budget_ou_accounts, account_list):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added successfully!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''- SubscriptionType: EMAIL
              Address: ''' + i + '''
            '''
                new_mails+= mail

            new_mails_1 = ''''''
            for i in mails:
                mail_1='''{
                "Type": "EMAIL",
                "Address": ''' + '"' + i + '"' + '''
                },
            '''
                new_mails_1+= mail_1
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget and Cost Anomaly Detection: Enable AWS Budget and Cost Anomaly Detection"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters: 
          LinkedAccount:
            §OU
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
            
  CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ §OU_2 ]
                    }
                }'

  CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                },
                §MAILS
            ]'''
            an_bdg = CustomTemplate(b)
            budget_anomaly_template = (an_bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', NEW_MAILS=new_mails, MAILS =new_mails_1, OU = budget_ou_accounts, OU_2 = account_list))
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Monitoring-"+new_budget_name+"--"+new_monitor_name,
            TemplateBody=budget_anomaly_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)
            
def budget_anomaly_full():
    print(blue + "You have chosen to set an alarm on the Organization's total budget and Anomaly Monitor on all services." + CEND)
    print(green + "\nTell me the exact name of the profile associated with the MANAGEMENT ACCOUNT located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
    
    client = session.client('ce')
    response = client.get_anomaly_monitors()
    monitor_types = [monitor_type["MonitorType"] for monitor_type in response["AnomalyMonitors"]]
    os.system("clear")
    if "DIMENSIONAL" in monitor_types:
        print(red + "An Anomaly Detection Monitor already exists on all the Organization's services.\n"+ CEND)
        menu_budget_anomaly()
    account_id = session.client('sts').get_caller_identity().get('Account')
    os.system("clear")
    print(green + "\nWell, now tell me the monthly budget that the organization is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")

    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    os.system("clear")
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)
    anomaly_detection_threshold = round(((budget/30)*30)/100, 2)    
    check_budget_anomaly_name(session, account_id)
    os.system("clear")
    print(green + "\nIn addition to the support email, would you like to receive a notification on the other email?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the alarm on the Budget and Anomaly Monitor.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget and Cost Anomaly Detection: Enable AWS Budget and Cost Anomaly Detection"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
  CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'DIMENSIONAL'
            MonitorDimension: 'SERVICE' 

  CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                }
            ]'''
            an_bdg = CustomTemplate(b)
            budget_anomaly_template = (an_bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription'))
        
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Monitoring-"+new_budget_name+"--"+new_monitor_name,
            TemplateBody=budget_anomaly_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Budget Alarm and Anomaly Detection Monitor successfully created!\n" + CEND)                         
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_budget_anomaly_full(new_budget_name, new_monitor_name, budget, anomaly_detection_threshold, session)
            print(blue + "Budget Alarm and Anomaly Detection Monitor successfully created!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0
            
def budget_anomaly_selective():
    print(blue + "You have chosen to set an Alarm on the Budget and Anomaly Monitor of a single Organization account." + CEND)   
    print(green + "\nTell me the exact name of the profile associated with the MANAGEMENT ACCOUNT located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])

    account_id = session.client('sts').get_caller_identity().get('Account')
    client = session.client('organizations')

    response = client.list_accounts()

    result = ""
    i = 0
    
    os.system("clear")
    print(green + "\nHere are the accounts present in the Organization:\n" + CEND)

    account_sp_names = [account_name["Name"] for account_name in response["Accounts"]]
    account_sp_ids = [account_name["Id"] for account_name in response["Accounts"]]
    for i in account_sp_names:    
        index = account_sp_names.index(i)
        result = result + str(index)+ " -- " + str(account_sp_names[index]) + " (" + str(account_sp_ids[index]) + ")"
        print(result + "\n")
        result = ""
    p=0
    while p==0:
        try:
            choice = int(input(green + "\nChoose an option: " + CEND))
            specific_account = account_sp_ids[choice]
            p=1
        except:
            print(red + "\nPlease enter a valid value!" + CEND)

    os.system("clear")
    print(green + "\nWell, now tell me the monthly budget that the organization is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI'll assume it's dollars ($).\n")

    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    os.system("clear")
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)
    anomaly_detection_threshold = round(((budget/30)*30)/100, 2)    
    check_budget_anomaly_name(session, account_id)
    os.system("clear")
    print(green + "\nIn addition to the support email, would you like to receive a notification on the other email?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the alarm on the Budget and Anomaly Monitor.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget and Cost Anomaly Detection: Enable AWS Budget and Cost Anomaly Detection"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters: 
          LinkedAccount:
            - §SPECIFIC_ACCOUNT
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
  CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ "§SPECIFIC_ACCOUNT" ]
                    }
                }'

  CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                }
            ]'''
            an_bdg = CustomTemplate(b)
            budget_anomaly_template = (an_bdg.substitute(SUPPORT_MAIL = support_mail ,BUDGET = budget, BUDGET_NAME=new_budget_name, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', SPECIFIC_ACCOUNT = specific_account))
        
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Monitoring-"+new_budget_name+"--"+new_monitor_name,
            TemplateBody=budget_anomaly_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Budget Alarm and Anomaly Detection Monitor successfully created!\n" + CEND)                         
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_budget_anomaly_selective(new_budget_name, new_monitor_name, budget, anomaly_detection_threshold, session, specific_account)
            print(blue + "Budget Alarm and Anomaly Detection Monitor successfully created!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0

def budget_anomaly_ou():
    print(blue + "You have chosen to set an Alarm on the Budget and Anomaly Monitor of a single Organization account." + CEND) 
    print(green + "\nTell me the exact name of the profile associated with the MANAGEMENT ACCOUNT located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
                
    account_id = session.client('sts').get_caller_identity().get('Account')
    client = session.client('organizations')
    response=client.list_roots()
    root_id = response['Roots'][0]['Id']
    response = client.list_organizational_units_for_parent(
        ParentId= root_id
        )
    ou_names = [ou_name["Name"] for ou_name in response["OrganizationalUnits"]]
    ou_ids = [ou_id["Id"] for ou_id in response["OrganizationalUnits"]]

    result = ""
    i = 0
    os.system("clear")
    print(green + "\nHere are the Organizational Units present with their accounts in brackets:\n" + CEND)
    for entry in ou_ids:
        response = client.list_accounts_for_parent(
        ParentId=entry
        )
        account_names = [account_name["Name"] for account_name in response["Accounts"]]    
        result += str(ou_ids.index(entry)) + " -- " + ou_names[i] + " " + str(account_names)
        i += 1
        print(result + "\n")
        result = ""
    p=0
    while p==0:
        try:
            choice = int(input(green + "\nChoose an option: " + CEND))
            choice = ou_ids[choice]
            p=1
            response = client.list_accounts_for_parent(
                ParentId=choice
                )
            account_ids = [account_id["Id"] for account_id in response["Accounts"]]
            if len(account_ids) == 0:
                print(red + "\nYou cannot associate an empty OU! Try again!" + CEND)
                p=0
        except:
            print(red + "\nPlease enter a valid value!" + CEND)

    budget_ou_accounts = ''''''
    for i in account_ids:
        id_account='''- ''' + i + '''
            '''
        budget_ou_accounts+= id_account
    
    account_list = ""            
    for i in account_ids:
        if i == account_ids[-1]:
            account_list += '"'+str(i)+'"'
        else:
            account_list += '"'+str(i)+'", '

    os.system("clear")
    print(green + "\nWell, now tell me the monthly budget that the organization is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")

    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    os.system("clear")
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)
    anomaly_detection_threshold = round(((budget/30)*30)/100, 2)    
    check_budget_anomaly_name(session, account_id)
    os.system("clear")
    print(green + "\nIn addition to the e-mail <" + support_mail + ">, would you like to receive a notification on the other e-mails?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the alarm on the Budget and Anomaly Monitor.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget and Cost Anomaly Detection: Enable AWS Budget and Cost Anomaly Detection"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters: 
          LinkedAccount:
            §OU
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
  CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ §OU_2 ]
                    }
                }'

  CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                }
            ]'''
            an_bdg = CustomTemplate(b)
            budget_anomaly_template = (an_bdg.substitute(SUPPORT_MAIL = support_mail ,BUDGET = budget, BUDGET_NAME=new_budget_name, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', OU = budget_ou_accounts, OU_2 = account_list))
        
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Monitoring-"+new_budget_name+"--"+new_monitor_name,
            TemplateBody=budget_anomaly_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Budget Alarm and Anomaly Detection Monitor successfully created!\n" + CEND)                         
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_budget_anomaly_ou(new_budget_name, new_monitor_name, budget, anomaly_detection_threshold, session, budget_ou_accounts, account_list)
            print(blue + "Budget Alarm and Anomaly Detection Monitor successfully created!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0

def menu_budget_anomaly():
    print(blue + '\nYou have chosen to set an alarm on the Budget and an Anomaly Detection Monitor.\n' + CEND)
    print_budget_anomaly_menu()
    option_2 = ''
    e=0
    while e==0:
        try:
            option_2 = int(input(green + '\nChoose an option: ' + CEND))
            e=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            e=0
        if option_2 == 1:
            os.system("clear")
            budget_anomaly_full()
        elif option_2 == 2:
            os.system("clear")
            budget_anomaly_selective()
        elif option_2 == 3:
            os.system("clear")
            budget_anomaly_ou()                   
        elif option_2 == 4:
            os.system("clear")
            menu_iniziale()
        else:
            if type(option_2) == int:
                print(red + "\nPlease enter a valid value!" + CEND)
            e=0

def check_anomaly_name(session):
    anomaly_detection = session.client('ce')
    describe_anomaly_monitors = anomaly_detection.get_anomaly_monitors()
    print(green + "\nNow you need to choose a name for the monitor." + CEND)
    try:
        monitor_names = [monitor_name["MonitorName"] for monitor_name in describe_anomaly_monitors["AnomalyMonitors"]]
        if len(monitor_names) == 0:
            print(blue + "\nThere are currently no other Anomaly Detection Monitors." + CEND) 
        else:
            print(blue + "\nAt the moment, the existing names are:\n" + CEND)
            for item in monitor_names:
                print(item)
    except:
        print(blue + "\nThere are currently no other Anomaly Detection Monitors." + CEND)     
    print(green + "\nEnter the name you want to give to the Anomaly Detection Monitor.\n" + CEND)
    global new_monitor_name   
    new_monitor_name=input()
    try:
        equal_elements=collections.Counter(monitor_names)[new_monitor_name]
    except:
        equal_elements=0   
    while equal_elements !=0:
        print(red + "\nA monitor with this name already exists." + CEND)
        print(red + "\nTry again, enter a different name:\n"+ CEND)
        new_monitor_name=input()
        equal_elements=collections.Counter(monitor_names)[new_monitor_name]
    return new_monitor_name

def new_subscriber_monitor_full(new_monitor_name, session, anomaly_detection_threshold):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added successfully!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''{
                "Type": "EMAIL",
                "Address": ''' + '"' + i + '"' + '''
                },
            '''
                new_mails+= mail
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Anomaly Detection Monitor.\n" + CEND)
            a='''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "Cost Monitoring: Enable Cost Anomaly Detection"
Resources:
    CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'DIMENSIONAL'
            MonitorDimension: 'SERVICE' 

    CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                },
                §MAILS
            ]'''
            an_det = CustomTemplate(a)
            an_detection_template = (an_det.substitute(SUPPORT_MAIL = support_mail, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', MAILS = new_mails))            
            
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Anomaly-Detection-"+new_monitor_name,
            TemplateBody=an_detection_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)

def new_subscriber_monitor_selective(new_monitor_name, session, anomaly_detection_threshold, specific_account):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added successfully!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''{
                "Type": "EMAIL",
                "Address": ''' + '"' + i + '"' + '''
                },
            '''
                new_mails+= mail
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Anomaly Detection Monitor.\n" + CEND)
            a='''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "Cost Monitoring: Enable Cost Anomaly Detection"
Resources:
    CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ "§SPECIFIC_ACCOUNT" ]
                    }
                }'

    CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                },
                §MAILS
            ]'''
            an_det = CustomTemplate(a)
            an_detection_template = (an_det.substitute(SUPPORT_MAIL = support_mail, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', MAILS = new_mails, SPECIFIC_ACCOUNT = specific_account))            
            
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Anomaly-Detection-"+new_monitor_name,
            TemplateBody=an_detection_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)

def new_subscriber_monitor_ou(new_monitor_name, session, anomaly_detection_threshold, account_list):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added successfully!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''{
                "Type": "EMAIL",
                "Address": ''' + '"' + i + '"' + '''
                },
            '''
                new_mails+= mail
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Anomaly Detection Monitor.\n" + CEND)
            a='''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "Cost Monitoring: Enable Cost Anomaly Detection"
Resources:
    CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ §OU ]
                    }
                }'

    CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                },
                §MAILS
            ]'''
            an_det = CustomTemplate(a)
            an_detection_template = (an_det.substitute(SUPPORT_MAIL = support_mail, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', MAILS = new_mails, OU = account_list ))            
            
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Anomaly-Detection-"+new_monitor_name,
            TemplateBody=an_detection_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)

def anomaly_detection_full():
    print(blue + "\nYou have chosen to set up an Anomaly Detection Monitor on all the organization's services." + CEND)
    print(green + "\nTell me the exact name of the profile associated with the MANAGEMENT ACCOUNT located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
                
    client = session.client('ce')
    response = client.get_anomaly_monitors()
    monitor_types = [monitor_type["MonitorType"] for monitor_type in response["AnomalyMonitors"]]
    os.system("clear")
    if "DIMENSIONAL" in monitor_types:
        print(red + "An Anomaly Detection Monitor already exists on all the organization's services.\n"+ CEND)
        menu_anomaly_detection()
        
    print(green + "\nWell, now tell me the monthly budget that the organization is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")

    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    os.system("clear")        
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)
    anomaly_detection_threshold = round(((budget/30)*30)/100, 2)    
    check_anomaly_name(session)        
    os.system("clear")

    print(green + "\nIn addition to the e-mail <" + support_mail + ">, would you like to receive a notification on the other e-mails?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Anomaly Detection Monitor.\n" + CEND)
            a='''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "Cost Monitoring: Enable Cost Anomaly Detection"
Resources:
    CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'DIMENSIONAL'
            MonitorDimension: 'SERVICE' 

    CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                }
            ]'''
            an_det = CustomTemplate(a)
            an_detection_template = (an_det.substitute(SUPPORT_MAIL = support_mail, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription'))            
            
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Anomaly-Detection-"+new_monitor_name,
            TemplateBody=an_detection_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Anomaly Detection Monitor successfully created!\n" + CEND)                          
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_monitor_full(new_monitor_name, session, anomaly_detection_threshold)
            print(blue + "Anomaly Detection Monitor successfully created!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0

def anomaly_detection_selective(): 
    print(blue + "\nYou have chosen to set up an Anomaly Detection Monitor on a single organization account." + CEND)
    print(green + "\nTell me the exact name of the profile located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
    
    client = session.client('organizations')

    response = client.list_accounts()

    result = ""
    i = 0
    
    os.system("clear")
    print(green + "\nHere are the accounts present in the Organization:\n" + CEND)

    account_sp_names = [account_name["Name"] for account_name in response["Accounts"]]
    account_sp_ids = [account_name["Id"] for account_name in response["Accounts"]]
    for i in account_sp_names:    
        index = account_sp_names.index(i)
        result = result + str(index)+ " -- " + str(account_sp_names[index]) + " (" + str(account_sp_ids[index]) + ")"
        print(result + "\n")
        result = ""
    p=0
    while p==0:
        try:
            choice = int(input(green + "\nChoose an option: " + CEND))
            specific_account = account_sp_ids[choice]
            p=1
        except:
            print(red + "\nPlease enter a valid value!" + CEND)

    os.system("clear")
    print(green + "\nNow tell me the monthly budget that the account in question is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")
    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)        
    anomaly_detection_threshold = round(((budget/30)*30)/100, 2)
    check_anomaly_name(session)    
    os.system("clear")
    print(green + "\nIn addition to the e-mail <" + support_mail + ">, would you like to receive a notification on the other e-mails?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Anomaly Detection Monitor.\n" + CEND)
            a='''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "Cost Monitoring: Enable Cost Anomaly Detection"
Resources:
    CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ "§SPECIFIC_ACCOUNT" ]
                    }
                }'
 
    CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                }
            ]'''
            an_det = CustomTemplate(a)
            an_detection_template = (an_det.substitute(SUPPORT_MAIL = support_mail, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', SPECIFIC_ACCOUNT = specific_account))            
            
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Anomaly-Detection-"+new_monitor_name,
            TemplateBody=an_detection_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Anomaly Detection Monitor successfully created!\n" + CEND)                                 
        
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_monitor_selective(new_monitor_name, session, anomaly_detection_threshold, specific_account)
            print(blue + "Anomaly Detection Monitor successfully created!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0
         
def anomaly_detection_ou(): 
    print(blue + "\nYou have chosen to set up an Anomaly Detection Monitor on all accounts related to an organization OU." + CEND)
    print(green + "\nTell me the exact name of the profile located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
                
    client = session.client('organizations')
    response=client.list_roots()
    root_id = response['Roots'][0]['Id']
    response = client.list_organizational_units_for_parent(
        ParentId= root_id
        )
    ou_names = [ou_name["Name"] for ou_name in response["OrganizationalUnits"]]
    ou_ids = [ou_id["Id"] for ou_id in response["OrganizationalUnits"]]

    result = ""
    i = 0
    os.system("clear")
    print(green + "\nHere are the Organizational Units present with their accounts in brackets:\n" + CEND)
    for entry in ou_ids:
        response = client.list_accounts_for_parent(
        ParentId=entry
        )
        account_names = [account_name["Name"] for account_name in response["Accounts"]]    
        result += str(ou_ids.index(entry)) + " -- " + ou_names[i] + " " + str(account_names)
        i += 1
        print(result + "\n")
        result = ""
    p=0
    while p==0:
        try:
            choice = int(input(green + "\nChoose an option: " + CEND))
            choice = ou_ids[choice]
            p=1
            response = client.list_accounts_for_parent(
                ParentId=choice
                )
            account_ids = [account_id["Id"] for account_id in response["Accounts"]]
            if len(account_ids) == 0:
                print(red + "\nYou cannot associate an empty OU! Try again!" + CEND)
                p=0
        except:
            print(red + "\nPlease enter a valid value!" + CEND)
    account_list = ""            
    for i in account_ids:
        if i == account_ids[-1]:
            account_list += '"'+str(i)+'"'
        else:
            account_list += '"'+str(i)+'", '
           
    os.system("clear")
    print(green + "\nNow tell me the monthly budget that the OU in question is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")
    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)        
    anomaly_detection_threshold = round(((budget/30)*30)/100, 2)
    check_anomaly_name(session)    
    os.system("clear")
    print(green + "\nIn addition to the e-mail <" + support_mail + ">, would you like to receive a notification on the other e-mails?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Anomaly Detection Monitor.\n" + CEND)
            a='''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "Cost Monitoring: Enable Cost Anomaly Detection"
Resources:
    CostAnomalyDetection:
        Type: 'AWS::CE::AnomalyMonitor'
        Properties:
            MonitorName: "§ANOMALY_DETECTION_NAME"
            MonitorType: 'CUSTOM'
            MonitorSpecification: '
                {
                    "Dimensions" : {
                    "Key" : "LINKED_ACCOUNT",
                    "Values" : [ §OU ]
                    }
                }'
 
    CostAnomalySubscription:
        Type: 'AWS::CE::AnomalySubscription'
        Properties:
            SubscriptionName: "§ANOMALY_SUBSCRIPTION_MAME"
            Threshold: §THRESHOLD
            Frequency: "DAILY"
            MonitorArnList: [
                !Ref CostAnomalyDetection
            ]
            Subscribers: [
                {
                "Type": "EMAIL",
                "Address": "§SUPPORT_MAIL"
                }
            ]'''
            an_det = CustomTemplate(a)
            an_detection_template = (an_det.substitute(SUPPORT_MAIL = support_mail, THRESHOLD = anomaly_detection_threshold, ANOMALY_DETECTION_NAME = new_monitor_name, ANOMALY_SUBSCRIPTION_MAME = new_monitor_name + '-Subscription', OU = account_list))            
            
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="Cost-Anomaly-Detection-"+new_monitor_name,
            TemplateBody=an_detection_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Anomaly Detection Monitor successfully created!\n" + CEND)                                 
        
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_monitor_ou(new_monitor_name, session, anomaly_detection_threshold, account_list)
            print(blue + "Anomaly Detection Monitor successfully created!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0         
               
def menu_anomaly_detection(): 
    print(blue + '\nYou have chosen to set up an Anomaly Detection Monitor.\n' + CEND)
    print_anomaly_detection_menu()
    option_2 = ''
    e=0
    while e==0:
        try:
            option_2 = int(input(green + '\nChoose an option: ' + CEND))
            e=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            e=0
        if option_2 == 1:
            os.system("clear")
            anomaly_detection_full()
        elif option_2 == 2:
            os.system("clear")
            anomaly_detection_selective()
        elif option_2 == 3:
            os.system("clear")
            anomaly_detection_ou()                        
        elif option_2 == 4:
            os.system("clear")
            menu_iniziale()
        else:
            if type(option_2) == int:
                print(red + "\nPlease enter a valid value!" + CEND)
            e=0

def check_budget_name(session, account_id):
    check_budget = session.client('budgets')
    DescribeBudget = check_budget.describe_budgets(AccountId=account_id)
    print(green + "\nNow you need to choose a name for the alarm." + CEND)
    try:
        budget_names = [budget_name["BudgetName"] for budget_name in DescribeBudget["Budgets"]]
        if len(budget_names) == 0:
            print(blue + "\nAt the moment there are no other alarms on the Budget." + CEND) 
        else:
            print(blue + "\nAt the moment, the existing names are:\n" + CEND)
            for item in budget_names:
                print(item)
    except:
        print(blue + "\nAt the moment there are no other alarms on the Budget." + CEND) 
    print(green + "\nEnter the name you want to give the budget alert.\n" + CEND)
    global new_budget_name
    new_budget_name=input()
    try:
        equal_elements=collections.Counter(budget_names)[new_budget_name]
    except:
        equal_elements=0
    while equal_elements !=0:
        print(red + "\nThere is already a Budget alert in the AWS Budget service of the account in question with this name." + CEND)
        print(red + "\nTry again, enter a different name:\n"+ CEND)
        new_budget_name=input()
        equal_elements=collections.Counter(budget_names)[new_budget_name]
    return new_budget_name

def new_subscriber_budget_full(new_budget_name, budget, session):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added successfully!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''- SubscriptionType: EMAIL
              Address: ''' + i + '''
            '''
                new_mails+= mail
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget: Enable AWS Budget"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS'''
            bdg = CustomTemplate(b)
            budget_template = (bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, NEW_MAILS=new_mails))
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="AWS-Budget-"+new_budget_name,
            TemplateBody=budget_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)           

def new_subscriber_budget_selective(new_budget_name, budget, session, specific_account):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added successfully!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''- SubscriptionType: EMAIL
              Address: ''' + i + '''
            '''
                new_mails+= mail
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget: Enable AWS Budget"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          LinkedAccount:
            - §SPECIFIC_ACCOUNT       
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL    
            §NEW_MAILS'''
            bdg = CustomTemplate(b)
            budget_template = (bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, NEW_MAILS=new_mails, SPECIFIC_ACCOUNT = specific_account))
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="AWS-Budget-"+new_budget_name,
            TemplateBody=budget_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)   
     
def new_subscriber_budget_ou(new_budget_name, budget, session, budget_ou_accounts):
    mails=[]
    print(green + "\nEnter the email you want to add:" + CEND)
    print("PS: You can then choose to add more.\n")
    new_mail=input()
    mails.append(new_mail)
    os.system("clear")
    print(blue + "The mail " + new_mail + " has been added successfully!" + CEND)
    y=0
    while y==0:
        print(green + "\nDo you want to insert a new email?" + CEND)
        print_mail_no_yes()
        mail_no_yes_option = ""
        l=0
        while l==0:
            try:
                mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
                l=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                l=0
        if mail_no_yes_option == 1:
            new_mails = ''''''
            for i in mails:
                mail='''- SubscriptionType: EMAIL
              Address: ''' + i + '''
            '''
                new_mails+= mail
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget: Enable AWS Budget"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          LinkedAccount:
            §OU        
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
            §NEW_MAILS'''
            bdg = CustomTemplate(b)
            budget_template = (bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, NEW_MAILS=new_mails, OU = budget_ou_accounts))
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="AWS-Budget-"+new_budget_name,
            TemplateBody=budget_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            y=1
        elif mail_no_yes_option == 2:
            print(green + "\nEnter the new email:\n" + CEND)
            new_mail_2=input()
            os.system("clear")
            print(blue + "The mail " + new_mail_2 + " has been added successfully!" + CEND)
            mails.append(new_mail_2)               
        
def budget_alarm_full():
    print(blue + "You have chosen to set an alarm on the Organization's total budget." + CEND)
    print(green + "\nTell me the exact name of the profile associated with the MANAGEMENT ACCOUNT located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
    account_id = session.client('sts').get_caller_identity().get('Account')
    os.system("clear")
    print(green + "\nWell, now tell me the monthly budget that the organization is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")

    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    os.system("clear")
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)
    check_budget_name(session, account_id)
    os.system("clear")
    print(green + "\nIn addition to the e-mail <" + support_mail + ">, would you like to receive a notification on the other e-mails?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget: Enable AWS Budget"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL'''
            bdg = CustomTemplate(b)
            budget_template = (bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name))
        
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="AWS-Budget-"+new_budget_name,
            TemplateBody=budget_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Budget alert created correctly!\n" + CEND)                         
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_budget_full(new_budget_name, budget, session)
            print(blue + "Budget alert created correctly!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0       

def budget_alarm_selective():
    print(blue + "You have chosen to set an alarm on the Budget of a single Organization account." + CEND)
    print(green + "\nTell me the exact name of the profile associated with the MANAGEMENT ACCOUNT located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
    account_id = session.client('sts').get_caller_identity().get('Account')
    client = session.client('organizations')

    response = client.list_accounts()

    result = ""
    i = 0
    
    os.system("clear")
    print(green + "\nHere are the accounts present in the Organization:\n" + CEND)

    account_sp_names = [account_name["Name"] for account_name in response["Accounts"]]
    account_sp_ids = [account_name["Id"] for account_name in response["Accounts"]]
    for i in account_sp_names:    
        index = account_sp_names.index(i)
        result = result + str(index)+ " -- " + str(account_sp_names[index]) + " (" + str(account_sp_ids[index]) + ")"
        print(result + "\n")
        result = ""
    p=0
    while p==0:
        try:
            choice = int(input(green + "\nChoose an option: " + CEND))
            specific_account = account_sp_ids[choice]
            p=1
        except:
            print(red + "\nPlease enter a valid value!" + CEND)

    os.system("clear")
    print(green + "\nWell, now tell me the monthly budget that the account is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")

    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    os.system("clear")        
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)
    check_budget_name(session, account_id)
    os.system("clear")
    print(green + "\nIn addition to the e-mail <" + support_mail + ">, would you like to receive a notification on the other e-mails?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget: Enable AWS Budget"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters: 
          LinkedAccount:
            - §SPECIFIC_ACCOUNT
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL'''
            bdg = CustomTemplate(b)
            budget_template = (bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, SPECIFIC_ACCOUNT = specific_account))
        
            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="AWS-Budget-"+new_budget_name,
            TemplateBody=budget_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Budget alert created correctly!\n" + CEND)                    
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_budget_selective(new_budget_name, budget, session, specific_account)
            print(blue + "Budget alert created correctly!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0

def budget_alarm_ou():
    print(blue + "You have chosen to set an alarm on the Budget on all accounts related to an OU of the organization." + CEND)
    print(green + "\nTell me the exact name of the profile associated with the MANAGEMENT ACCOUNT located in your local .aws folder.\n" + CEND)
    profile = input()
    while profile == "":
        print(red + "\nYou have not entered anything! Try again!\n" + CEND)
        profile = input()
    profile_ok = 0
    while profile_ok == 0:
        try:
            session=boto3.Session(profile_name=profile)
            profile_ok = 1             
        except botocore.exceptions.ProfileNotFound or botocore.exceptions.NoCredentialsError as error:
            print(red + "\nThe chosen profile name is incorrect. Try again!\n" + CEND)
            profile = input()
        if profile_ok == 1:
            try:
                sts = session.client('sts')
                identity = sts.get_caller_identity()
            except botocore.exceptions.UnauthorizedSSOTokenError:
                subprocess.run(['aws','sso', 'login', '--profile', profile])
    account_id = session.client('sts').get_caller_identity().get('Account')
    
    client = session.client('organizations')
    response=client.list_roots()
    root_id = response['Roots'][0]['Id']
    response = client.list_organizational_units_for_parent(
        ParentId= root_id
        )
    ou_names = [ou_name["Name"] for ou_name in response["OrganizationalUnits"]]
    ou_ids = [ou_id["Id"] for ou_id in response["OrganizationalUnits"]]

    result = ""
    i = 0
    os.system("clear")
    print(green + "\nHere are the Organizational Units present with their accounts in brackets:\n" + CEND)
    for entry in ou_ids:
        response = client.list_accounts_for_parent(
        ParentId=entry
        )
        account_names = [account_name["Name"] for account_name in response["Accounts"]]    
        result += str(ou_ids.index(entry)) + " -- " + ou_names[i] + " " + str(account_names)
        i += 1
        print(result + "\n")
        result = ""
    p=0
    while p==0:
        try:
            choice = int(input(green + "\nChoose an option: " + CEND))
            choice = ou_ids[choice]
            p=1
            response = client.list_accounts_for_parent(
                ParentId=choice
                )
            account_ids = [account_id["Id"] for account_id in response["Accounts"]]
            if len(account_ids) == 0:
                print(red + "\nYou cannot associate an empty OU! Try again!" + CEND)
                p=0
        except:
            print(red + "\nPlease enter a valid value!" + CEND)

    budget_ou_accounts = ''''''
    for i in account_ids:
        id_account='''- ''' + i + '''
            '''
        budget_ou_accounts+= id_account     
    os.system("clear")
    print(green + "\nWell, now tell me the monthly budget that the account is able to support WITHOUT THE CURRENCY." + CEND)
    print("\nI will assume they are dollars ($).\n")

    i=0
    while i==0:
        try: 
            budget_str=input()
            budget=float(budget_str)
            i=1
        except:
            print(red + "\nYou have not entered a valid value! Try again!\n" + CEND)
            i=0
    os.system("clear")        
    print(blue + "\nThe budget we will work on is therefore " + str(budget) + "$." + CEND)
    check_budget_name(session, account_id)
    os.system("clear")
    print(green + "\nIn addition to the e-mail <" + support_mail + ">, would you like to receive a notification on the other e-mails?" + CEND)
    print_mail_no_yes()
    mail_no_yes_option = ""
    n=0
    while n==0:
        try:
            mail_no_yes_option = int(input(green + '\nChoose an option: ' + CEND))
            n=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            n=0
        if mail_no_yes_option == 1:
            os.system("clear")
            print(blue + "\nI proceed with the creation of the Budget alert with the AWS Budget service.\n" + CEND)
            b = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: "AWS Budget: Enable AWS Budget"
Resources:
  AWSBudget:
    Type: "AWS::Budgets::Budget"
    Properties:
      Budget:
        BudgetName: §BUDGET_NAME
        BudgetLimit:
          Amount: §BUDGET
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters: 
          LinkedAccount:
            §OU
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 95
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            ThresholdType: PERCENTAGE
            Threshold: 100
          Subscribers:
            - SubscriptionType: EMAIL
              Address: §SUPPORT_MAIL'''
            bdg = CustomTemplate(b)
            budget_template = (bdg.substitute(SUPPORT_MAIL = support_mail, BUDGET = budget, BUDGET_NAME=new_budget_name, OU = budget_ou_accounts))

            client = session.client('cloudformation', region_name="us-east-1")
            response = client.create_stack(
            StackName="AWS-Budget-"+new_budget_name,
            TemplateBody=budget_template,
            Capabilities=[
            'CAPABILITY_NAMED_IAM',
            ],
            EnableTerminationProtection=True
            )
            print(blue + "Budget alert created correctly!\n" + CEND)                    
        elif mail_no_yes_option == 2:
            os.system("clear")
            new_subscriber_budget_ou(new_budget_name, budget, session, budget_ou_accounts)
            print(blue + "Budget alert created correctly!\n" + CEND)
        else:
            if type(mail_no_yes_option) == int:
                print(red + "Please enter a valid value:" + CEND)
            n=0
            
def menu_budget_alarm():    
    print(blue + '\nYou have chosen to set an alarm on the Budget.\n' + CEND)
    print_budget_alarm_menu()
    option_2 = ''
    e=0
    while e==0:
        try:
            option_2 = int(input(green + '\nChoose an option: ' + CEND))
            e=1
        except:
            print(red + '\nUnacceptable input. Please enter a number.' + CEND)
            e=0
        if option_2 == 1:
            os.system("clear")
            budget_alarm_full()
        elif option_2 == 2:
            os.system("clear")
            budget_alarm_selective()
        elif option_2 == 3:
            os.system("clear")
            budget_alarm_ou()                   
        elif option_2 == 4:
            os.system("clear")
            menu_iniziale()
        else:
            if type(option_2) == int:
                print(red + "\nPlease enter a valid value!" + CEND)
            e=0 
       

def menu_iniziale():
    print(green + "\nHere's the menu:\n" + CEND)
    if __name__=='__main__':
        print_menu()
        option = ''
        u=0
        while u==0:
            try:
                option = int(input(green + '\nChoose an option: ' + CEND))
                u=1
            except:
                print(red + '\nUnacceptable input. Please enter a number.' + CEND)
                u=0
            if option == 1:
                os.system('clear')
                menu_budget_alarm()
            elif option == 2:
                os.system("clear")
                menu_anomaly_detection()
            elif option == 3:
                os.system("clear")
                menu_budget_anomaly() 
            elif option == 4:
                os.system("clear")
                print(blue + "\nBye!\n" + CEND)
            else:
                if type(option) == int:
                    print(red + "\nPlease enter a valid value!" + CEND)
                u=0     


### INITIAL PHASE
os.system("clear")
print(cyan + "\nWelcome to the cost monitoring automation tool." + CEND)
menu_iniziale()
            
