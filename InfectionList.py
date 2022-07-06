# -*- coding: utf-8 -*-

from flask_restful import abort, Resource, request
from sqlalchemy.orm import scoped_session
import binascii
import ctypes


from helper import helper
from db_session import db_session_factory_global
from helper import db_session_helper
from IkLogger import CMyIkLogger
from InfectionDetails import InfectionDetailsSpecific


#/admin/infections [GET]
class InfectionList(Resource):
    def __init__(self, import_name='InfectionList'):
        super(InfectionList, self).__init__()
        self.__name__ = import_name

    def get(self):
        try:
            providerName = helper.getCurrentRequestProviderName()
            if providerName is None:
                return "Bad Request! Providername not found!", 404

            db_session_global_sess = scoped_session(db_session_factory_global._sessionmaker)
            db_session_global = db_session_helper(db_session_global_sess(autocommit=True),db_session_factory_global._Tables, db_session_factory_global.tables_raw)

            data = 0
            cacheID = 0
            try:
                if not (request is None) and not (request.args) is None and len(request.args) > 0:
                    if len(request.args.getlist('cacheID')) > 0:
                        cacheID = int(request.args.getlist('cacheID')[0])
            except:
                cacheID = 0

            try:
                if not (request is None) and not (request.args) is None and len(request.args) > 0:
                    if len(request.args.getlist('data')) > 0:
                        data = int(request.args.getlist('data')[0])
            except:
                data = int(0)

            rowProvider = db_session_global.session.query(db_session_global.tables_raw['T_PROVIDER']).filter( \
                     db_session_global.tables_raw['T_PROVIDER'].columns.providername == providerName).first()

            maxCacheID = 0
            try:
                result = db_session_global.session.execute("select MAX(CAST(i.rv as bigint)) as rvINT from T_AVIC_INFECTION_INFO i join T_AVIC_DEVICE d on d.device_id=i.device_id\
                                                            WHERE d.clientnr in (select clientnr from T_PROVIDER_CLIENT where providernr = :pnr )", {'pnr': rowProvider.providernr})
                maxCacheID = result.fetchone()[0]
            except:
                maxCacheID = 0

            rows = db_session_global.session.execute("select i.device_id from T_AVIC_INFECTION_INFO i join T_AVIC_DEVICE d on d.device_id=i.device_id \
                    WHERE d.clientnr in (select clientnr from T_PROVIDER_CLIENT where providernr = :pnr ) AND CAST(i.rv as bigint) > :rv_int group by i.device_id ",\
                                                     {'pnr': rowProvider.providernr, 'rv_int': cacheID })
            if rows is None:
                return {}, 204

            infections = {}
            if data == 1:
                infections['data'] = []
            else:
               infections['deviceID'] = []
            infections['cacheID'] = maxCacheID

            specInfection = InfectionDetailsSpecific()
            for rowDevice in rows:
                DeviceID = rowDevice.device_id.urn[-36:]
                #deviceDetails = db_session_global.session.execute("SELECT * FROM T_AVIC_DEVICE WHERE device_id = :dID", {'dID': DeviceID}).first()
                if data == 1:
                    rowsInf = db_session_global.session.execute("select * from T_AVIC_INFECTION_INFO i \
                                                        WHERE device_id = :dID AND CAST(i.rv as bigint) > :rv_int ", \
                                                        { 'dID': DeviceID, 'rv_int': cacheID } )
                    if not (rowsInf is None):
                        infectionData = {}
                        infectionData['device_id'] = DeviceID
                        infectionData['infections'] = []
                        infectionData_infections = None

                        for row in rowsInf:
                            '''
                            # performance issues!!
                            infectionData_infections = specInfection.get(DeviceID, row.infection_id)
                            infectionData['infections'].append(infectionData_infections[0])
                            '''

                            #performance: 32% faster than code above
                            row_JSON = {}
                            row_JSON['infection_id'] = row.infection_id
                            row_JSON['sigid'] = row.sigid
                            row_JSON['signame'] = row.signame
                            row_JSON['full_path'] = row.full_path
                            row_JSON['process_name'] = row.process_name

                            if row.md5 is None:
                                row_JSON['md5'] = None
                            else:
                                md5 = binascii.hexlify(row.md5)
                                row_JSON['md5'] = str(md5, encoding='iso_8859_1')

                            row_JSON['crc64'] = ctypes.c_uint64(row.crc64).value
                            row_JSON['date_found'] = helper.alchemyencoder(row.date_found)
                            row_JSON['type_found'] = row.type_found
                            row_JSON['filesize'] = ctypes.c_uint64(row.filesize).value
                            infectionData['infections'].append(row_JSON)

                        infections['data'].append(infectionData)

                else:
                    infections['deviceID'].append(DeviceID)

            if data == 1:
                if len(infections['data']) > 0:
                    return infections, 200
            else:
                if len(infections['deviceID']) > 0:
                    return infections, 200

            if data == 1:
                return { 'cacheID': maxCacheID, 'data': [] }, 200
            else:
                return {'cacheID': maxCacheID, 'deviceID': [] }, 200
        except Exception as Ex:
            CMyIkLogger.warning("Error while getting global infections! ErrStr: "+str(Ex))
            abort(500, message="Internal Server Error!")

        finally:
            try:
                db_session_global_sess.remove()
            except:
                print("")