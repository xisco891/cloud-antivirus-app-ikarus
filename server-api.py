# -*- coding: utf-8 -*-

from flask import Flask, request, make_response
from flask_restful import Api, Resource
import json
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from IkLogger import CMyIkLogger
from helper import helper
import LicenseManagement
import DeviceLicenseManagement
import DeviceManagement
import InfectionDetails
import Info
import InfectionList
import Provisioning



#'/admin/licenses',methods=['get', 'post']
class PrintHeader(Resource):
    
    def __init__(self, import_name='PrintHeader'):
      
        super(PrintHeader, self).__init__()
        self.__name__ = import_name

    def get(self):
        try:
            if not (request is None):
                Header = {}
                for header in request.headers.environ:
                    if header.startswith("HTTP"):
                        Header[header] = str(request.headers.environ[header])+'<br>'

                strHeader = json.dumps(Header)
                #return Header, 200
                resp = make_response(strHeader,200)
                resp.content_type = 'text/html; charset=utf-8'
                return resp
                #return strHeader, 200
        except Exception as Ex:
            return "ERROR", 200

class BaseAPI(Flask):
  
    def __init__(self, import_name):
        super(BaseAPI, self).__init__(import_name=__name__)

        #self.APP = self
        self.API = Api(self)

        self.before_request(self._before_request)
        self.after_request(self._after_request)

        #self.Auth = server.Auth.Auth()
        #self.Protected = server.Auth.Protected()

        self.ServerLicenseManagementSpecific_provisioning = server.LicenseManagement.LicenseManagementSpecific(import_name='ServerLicenseManagementSpecific_provisioning')
        self.ServerLicenseManagementSpecific = server.LicenseManagement.LicenseManagementSpecific()
        self.ServerLicenseManagementGlobal = server.LicenseManagement.LicenseManagementGlobal()

        self.ServerDeviceLicenseManagementSpecific = server.DeviceLicenseManagement.DeviceLicenseManagementSpecific()
        self.ServerDeviceLicenseManagementGlobal = server.DeviceLicenseManagement.DeviceLicenseManagementGlobal()

        self.ServerDeviceManagementSpecific = server.DeviceManagement.DeviceManagementSpecific()
        self.DeviceManagementGlobal = server.DeviceManagement.DeviceManagementGlobal()

        self.ServerInfectionDetailsSpecific = server.InfectionDetails.InfectionDetailsSpecific()
        self.ServerInfectionDetailsGlobal = server.InfectionDetails.InfectionDetailsGlobal()
        self.ServerInfectionList = server.InfectionList.InfectionList()

        self.ServerPrintHeader = PrintHeader()
        self.VersionInfo = server.Info.VersionInfo()
        self.VersionInfo_Nagios = server.Info.VersionInfo(import_name='VersionInfo_Nagios')

        #self.Provisioning = server.Provisioning.Provisioning()
        self.Provisioning = server.Provisioning.Provisioning(import_name='Provisioning')
        self.Provisioning_mail = server.Provisioning.Provisioning(import_name='Provisioning_mail')
        self.Provisioning_web = server.Provisioning.Provisioning(import_name='Provisioning_web')
        self.Provisioning_wifi = server.Provisioning.Provisioning(import_name='Provisioning_wifi')
        self.Provisioning_mobile = server.Provisioning.Provisioning(import_name='Provisioning_mobile')
        self.Provisioning_av = server.Provisioning.Provisioning(import_name='Provisioning_av')

        self.LoginUrlSSO = server.Provisioning.LoginUrl()

    def _before_request(self):
        return helper.Log_before_request(request)

    def _after_request(self, response):
        return helper.Log_after_request(response, request)

    def AddDefaultServerRoutes(self):
        ###### BEGIN SERVER-API ######
        # CLOUD SECURITY
        #self.API.add_resource(self.Auth, '/auth/login', methods=['get', 'post'])
        #self.API.add_resource(self.Protected, '/user/<url_param>', methods=['get', 'post'])

        # LICENSE MANAGEMENT

        self.API.add_resource(self.ServerPrintHeader, '/admin/header', methods=['get'])

        self.API.add_resource(self.ServerLicenseManagementGlobal, '/admin/licenses',methods=['get', 'post'])
        self.API.add_resource(self.ServerLicenseManagementSpecific, '/admin/licenses/<TID>',methods=['get', 'delete', 'patch'])
        self.API.add_resource(self.ServerLicenseManagementSpecific_provisioning, '/admin/licenses/<TID>/provisioning', methods=['get', 'post'])
        # server.API.add_resource(server.LicenseManagementSpecific, '/admin/licenses', defaults={'TID': None}, methods=('get', 'delete', 'post'))

        # DEVICE LICENSE MANAGEMENT
        self.API.add_resource(self.ServerDeviceLicenseManagementGlobal, '/admin/licenses/<TID>/devices',methods=['get', 'post'])
        self.API.add_resource(self.ServerDeviceLicenseManagementSpecific,'/admin/licenses/<TID>/devices/<DeviceID>', methods=['get', 'delete', 'put'])

        # DEVICE MANAGEMENT
        self.API.add_resource(self.DeviceManagementGlobal, '/admin/devices', methods=['get'])
        self.API.add_resource(self.ServerDeviceManagementSpecific, '/admin/devices/<DeviceID>',methods=['get', 'delete'])

        # INFECTION DETAILS
        self.API.add_resource(self.ServerInfectionDetailsGlobal, '/admin/devices/<DeviceID>/infections',methods=['get'])
        self.API.add_resource(self.ServerInfectionDetailsSpecific,'/admin/devices/<DeviceID>/infections/<InfectionID>', methods=['get'])

        self.API.add_resource(self.VersionInfo, '/admin/info/version', methods=['get'])
        self.API.add_resource(self.VersionInfo_Nagios, '/admin/info/nagios', methods=['get'])

        # GLOBAL INFECTION LIST
        self.API.add_resource(self.ServerInfectionList, '/admin/infections', methods=['get'])
        ###### END SERVER-API ######

        #PROVISIONING
        self.API.add_resource(self.Provisioning_mail, '/admin/provisioning/mail', methods=['post', 'patch', 'put','delete'])
        self.API.add_resource(self.Provisioning_web, '/admin/provisioning/web', methods=['post', 'patch', 'put', 'delete'])
        self.API.add_resource(self.Provisioning_wifi, '/admin/provisioning/wifi', methods=['post', 'patch', 'put', 'delete'])
        self.API.add_resource(self.Provisioning_mobile, '/admin/provisioning/mobile', methods=['post', 'patch', 'put', 'delete'])
        self.API.add_resource(self.Provisioning_av, '/admin/provisioning/av', methods=['post', 'patch', 'put', 'delete'])
        self.API.add_resource(self.Provisioning, '/admin/provisioning', methods=['delete', 'get'])
        self.API.add_resource(self.LoginUrlSSO, '/admin/login/url', methods=['get', 'post'])



baseAPI = BaseAPI(__name__)
baseAPI.AddDefaultServerRoutes()

if __name__ == '__main__':
    CMyIkLogger.info("INFO - TEST")

    #starts the listener
    baseAPI.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
