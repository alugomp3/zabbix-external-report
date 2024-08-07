from pyzabbix import ZabbixAPI
from datetime import datetime,timedelta
import jinja2

def getAuth():
  # Set up the Zabbix API connection
  zabbix_url = ''
  zabbix_user = ''
  zabbix_password = ''
  return ZabbixAPI(url=zabbix_url,user=zabbix_user,password=zabbix_password)

def getTimestamp(value=None):
   if value:
     return int((datetime.now() - timedelta(value)).timestamp())
   else:
     now = datetime.today()
     return int(datetime.timestamp(now))


def convertTB(value):
  BYTES_POR_TEBIBYTE = 1024 ** 4
  return round((int(value) / BYTES_POR_TEBIBYTE), 2)

def calcPercGrowth(values):
  overall = 0
  for value in values:
    print(value['itemid'],convertTB(value['value']))
    overall = overall

    return sizeDB

def getSizeDB():
  zabbix_api = getAuth()
  latestValue = 0
  values = zabbix_api.history.get(itemids='2873073', time_from=getTimestamp(1),time_till=getTimestamp(), history='3')
  for entry in values:
    latestValue = entry['value']
  return convertTB(latestValue)

def getDiffSize():
  zabbix_api = getAuth()
  values = zabbix_api.history.get(itemids='2873073', time_from=getTimestamp(31),time_till=getTimestamp(), history='3')
  return calcSizeDB(values)

def getRelatorio(days=None):
  zabbix_api = getAuth()

  # Get Version
  version = zabbix_api.apiinfo.version()

  if version == '5.4.12':
    # Get the IT service ID

    #Dict of Services
    service_dict = {'DB': 'Banco de Dados', 'FW': 'Firewall', 'DNS': 'DNS', 'Ldap': 'Ldap', 'Storage': 'Storage'}

    for service_id, service_name in service_dict.items():
      service = zabbix_api.service.get(filter={'name': service_name})[0]
      service_id = service['serviceid']

      start_date = datetime.now() - timedelta(30)
      start_date2 = datetime.now() - timedelta(1)
      now = datetime.today()
      end_date = datetime.timestamp(now)

      # Get the IT service availability report for the last 30 days
      report = zabbix_api.service.getsla(serviceids=[service_id], intervals={'from': int(datetime.timestamp(start_date)), 'to': int(datetime.timestamp(now))}, operations=[{'operationid': 'service_availability'}], extendoutput=True)
      ###report = zabbix_api.sla.getsli(serviceids=[service_id], period_from=int(datetime.timestamp(start_date)),period_to=int(datetime.timestamp(now)),slaid='4')
      populateJinja2(report)

  else:
    # Get the IT service ID
    service_name = 'Backbone Principal (Infraestrutura)'
    service = zabbix_api.service.get(filter={'name': service_name})[0]
    service_id = service['serviceid']

    start_date = datetime.now() - timedelta(30)
    now = datetime.today()
    end_date = datetime.timestamp(now)

    # Get the IT service availability report for the last 30 days
    #report = zabbix_api.service.getsla(serviceids=[service_id], intervals={'from': 'now-30d', 'to': 'now'}, operations=[{'operationid': 'service_availability'}], extendoutput=True)
    report = zabbix_api.sla.getsli(serviceids=[service_id], period_from=getTimestamp(30),period_to=getTimestamp(),slaid='4')
    print(report)


# Caso Python3.10 for usado
#def serviceName(name):
#  match name:
#    case 184:
#      return "Banco de Dados"
#    case 212:
#      return "Firewall"
#    case 196:
#      return "DNS"
#    case 229:
#      return "Ldap"
#    case 235:
#      return "Storage"
#    case _:
#      return "Serviço não registrado"

def serviceName(name):
  if name == '184':
      return "Banco de Dados"
  elif name == '212':
      return "Firewall"
  elif name == '196':
      return "DNS"
  elif name == '229':
      return "Ldap"
  elif name == '235':
      return "Storage"
  else:
      return "Serviço não registrado"

def populateJinja2(report):
    """
    Renderiza o template do relatorio
    """
    first_key = next(iter(report), None)
    reportsValue = report[first_key]
    sla_list = reportsValue.get('sla', [])
    sla = sla_list[0]

    print(getSizeDB())
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "layout.html"
    template = template_env.get_template(template_file)
    output_text = template.render(
        name=serviceName(first_key),
        inicio=sla['from'],
        final=sla['to'],
        sla=sla['sla'],
        okTime=sla['okTime'],
        downtimeTime=sla['downtimeTime'],
        problemTime=sla['problemTime']
        )

    html_path = f'{serviceName(first_key)}.html'
    html_file = open(html_path, 'w')
    html_file.write(output_text)
    html_file.close()

getRelatorio()
