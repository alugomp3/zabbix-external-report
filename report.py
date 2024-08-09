from pyzabbix import ZabbixAPI
from datetime import datetime,timedelta
from docxtpl import DocxTemplate
import jinja2
import logging

service_dict = {'DB': 'Banco de Dados'}

service_list = ['Banco de Dados']

def getMonth(value):
  months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
  return months[value-1]


def getAuth():
  # Set up logging
  logging.basicConfig(level=logging.ERROR)
  # Set up the Zabbix API connection
  zabbix_url = ''
  zabbix_user = ''
  zabbix_password = ''
  try:
    return ZabbixAPI(url=zabbix_url,user=zabbix_user,password=zabbix_password)
  except ConnectionError:
    print("Erro de conexão com Zabbix")
  except AuthenticationError:
    print("Falha na autenticação com Zabbix")
  except Exception as e:
    logging.error(f"Erro ao conectar com Zabbix: {e}")

def getTimestamp(value=None):
   if value:
     return int((datetime.now() - timedelta(value)).timestamp())
   else:
     now = datetime.today()
     return int(datetime.timestamp(now))

def getSlaIndex(report):
  first_key = next(iter(report), None)
  reportsValue = report[first_key]
  sla_list = reportsValue.get('sla', [])
  sla = sla_list[0]
  return first_key, sla

def roundValue(value):
  return round(value, 2)

def calcMinutes(value):
  return round(value / 60 , 2)

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
  values = zabbix_api.history.get(itemids='00000', time_from=getTimestamp(1),time_till=getTimestamp(), history='3')
  for entry in values:
    latestValue = entry['value']
  return convertTB(latestValue)

def getDiffSize(days=30):
  zabbix_api = getAuth()
  values = zabbix_api.history.get(itemids='00000', time_from=getTimestamp(days),time_till=getTimestamp(), history='3')
  return calcSizeDB(values)

  #groupFilter = {'name': 'MyHostGroup'}
  #itemFilter = {'name': 'ICMP Loss'}

  # Get the hostgroup id by its name
  #hostgroups = zapi.hostgroup.get(filter=groupFilter, output=['groupids', 'name'])

  # Get the hosts of the hostgroup by hostgroup id
  #hosts = zapi.host.get(groupids=hostgroups[0]['groupid'])

  #for host in (hosts):
    # Get the item info (not the values!) by item name AND host id
    #items = zapi.item.get(filter=itemFilter, host=host['host'], output='extend', selectHosts=['host', 'name'])

    # for loop - for future fuzzy search, otherwise don't loop and use items[0]
    #for item in items:
      # Get item values
      #values = zapi.history.get(itemids=item['itemid'], time_from=fromTimestamp, time_till=tillTimestamp, history=item['value_type'])
      #for historyValue in values:
      #    print( ......... ) # format here your output, values are stored in historyValue['value']



def getRelatorio(service=None,days=30):
  zabbix_api = getAuth()

  # Get Version
  version = zabbix_api.apiinfo.version()

  if version == '5.4.12':
    if service:
      service = zabbix_api.service.get(filter={'name': service})[0]
      service_id = service['serviceid']
      service = zabbix_api.service.getsla(serviceids=[service_id], intervals={'from': getTimestamp(days), 'to': getTimestamp()}, operations=[{'operationid': 'service_availability'}], extendoutput=True)
      return service
    else:
      report_dict = {}
      for service_id, service_name in service_dict.items():
        service = zabbix_api.service.get(filter={'name': service_name})[0]
        service_id = service['serviceid']
        # Get the IT service availability report for the last X days
        report = zabbix_api.service.getsla(serviceids=[service_id], intervals={'from': getTimestamp(days), 'to': getTimestamp()}, operations=[{'operationid': 'service_availability'}], extendoutput=True)
        report_dict.update(report)
      return report_dict


  else:
    # Get the IT service ID
    report_dict = {}
    for service_id, service_name in service_dict.items():
      service = zabbix_api.service.get(filter={'name': service_name})[0]
      service_id = service['serviceid']
      # Get the IT service availability report for the last X days
      report = zabbix_api.sla.getsli(serviceids=[service_id], period_from=getTimestamp(days),period_to=getTimestamp(),slaid='4')
      report_dict.update(report)
    return report_dict


# Caso Python3.10 for usado
#def serviceName(name):
#  match name:
#    case 123:
#      return "Banco de Dados"
#    case _:
#      return "Serviço não registrado"

def serviceName(name):
  if name == '123':
      return "Banco de Dados"
  else:
      return "Serviço não registrado"

def populateReportsHtml(report):
    """
    Renderiza o template do relatorio
    """
    first_key, sla = getSlaIndex(report)

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

def populateReportsDocx(report):
    """
    Renderiza o template do relatorio
    """
    first_key, sla = getSlaIndex(report)

    doc = DocxTemplate("Modelo.docx")
    context = { 'name' : serviceName(first_key),'inicio': sla['from'], 'final': sla['to'], 'sla': sla['sla'], 'okTime': sla['okTime'], 'downtimeTime': sla['downtimeTime'], 'problemTime': sla['problemTime']}
    doc.render(context)
    doc.save(f"{serviceName(first_key)}.docx")

def populateAvailabilityDocx():
    """
    Renderiza o template do relatorio disponibilidade
    """

    context_dict = {}
    for service in service_list:
      report = getRelatorio(service)
      first_key, sla = getSlaIndex(report)

      serviceObj = {}
      serviceObj['sla'] = roundValue(sla['sla'])
      serviceObj['problemTime'] = calcMinutes(sla['problemTime'])
      context_dict[first_key] = serviceObj

    doc = DocxTemplate("Modelo.docx")
    context = {'db_sla': context_dict['123']['sla'],
    'mes': getMonth(datetime.today().month),
    'ano': datetime.today().year,
    'Pessoas': '',
    'dataHoje': datetime.now().strftime('%d-%m-%Y'),
    'principaisInterrupcoes': None,
    'acoesDispo': None,
    'recomendacoes': None,
    'conclusao': None}

    doc.render(context)
    doc.save("Relatorio.docx")
