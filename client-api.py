# -*- coding: utf-8 -*-

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from IkLogger import CMyIkLogger

import DeviceManagement
import LicenseManagement
import InfectionInformation
import StatusInformation

from flask import Flask, request
from flask_restful import Api
from helper import helper


class BaseAPI(Flask):
    def __init__(self, import_name):
        super(BaseAPI, self).__init__(import_name=__name__)

        #self.db_session = ThreadsafeSession()

        #self.APP = self
        self.API = Api(self)

        self.before_request(self._before_request)
        self.after_request(self._after_request)
        #CLIENT
        self.ClientDeviceManagementSpecific = client.DeviceManagement.DeviceManagementSpecific()
        self.ClientDeviceManagementGlobal = client.DeviceManagement.DeviceManagementGlobal()

        self.ClientLicenseManagement = client.LicenseManagement.ClientLicenseManagement()

        self.ClientInfectionInformationGlobal = client.InfectionInformation.CInfectionInformationGlobal()
        self.ClientInfectionInformationSpecific = client.InfectionInformation.CInfectionInformationSpecific()

        self.ClientStatusInformation_versions = client.StatusInformation.ClientStatusInformation(import_name='ClientStatusInformation_versions')
        self.ClientStatusInformation_settings = client.StatusInformation.ClientStatusInformation(import_name='ClientStatusInformation_settings')
        self.ClientStatusInformation_infections = client.StatusInformation.ClientStatusInformation(import_name='ClientStatusInformation_infections')

        #self.VersionInfo_Nagios = server.Info.VersionInfo(import_name='VersionInfo_Nagios')

    def _before_request(self):
        return helper.Log_before_request(request)

    def _after_request(self, response):
        return helper.Log_after_request(response, request)

    def AddDefaultClientRoutes(self):
        ###### BEGIN CLIENT-API ######
        self.API.add_resource(self.ClientDeviceManagementGlobal, '/client/devices', methods=['post'])
        self.API.add_resource(self.ClientDeviceManagementSpecific, '/client/devices/<DeviceID>',methods=['get', 'patch', 'delete'])

        self.API.add_resource(self.ClientLicenseManagement, '/client/devices/<DeviceID>/license',methods=['post', 'get', 'delete'])

        self.API.add_resource(self.ClientInfectionInformationGlobal, '/client/devices/<DeviceID>/infections',methods=['get'])
        self.API.add_resource(self.ClientInfectionInformationSpecific, '/client/devices/<DeviceID>/infections/<InfectionID>',methods=['post', 'patch', 'delete'])

        self.API.add_resource(self.ClientStatusInformation_versions, '/client/devices/<DeviceID>/versions', methods=['post'])
        self.API.add_resource(self.ClientStatusInformation_settings, '/client/devices/<DeviceID>/settings',methods=['post'])
        self.API.add_resource(self.ClientStatusInformation_infections, '/client/devices/<DeviceID>/infections',methods=['post'])

        #self.API.add_resource(self.VersionInfo, '/client/info/nagios', methods=['get'])
        ###### END CLIENT-API ######


baseAPI = BaseAPI(__name__)
baseAPI.AddDefaultClientRoutes()

if __name__ == '__main__':
    CMyIkLogger.info("INFO - TEST")

    #starts the listener
    baseAPI.run(host='127.0.0.1', port=5001, debug=True, threaded=True)
    #baseAPI.run(host='dew-tahiraj.ik.local', port=5001, debug=True, threaded=True)