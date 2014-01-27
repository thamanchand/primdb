#!/usr/local/bin/python
# ------------------------------------------------------------------------------
# Name:         mzML parser
# Purpose:      Parser for MS-based Proteomics mzML file, parses the selected mzML
#               elements information into the database.
# Author:      Thaman Chand (thamanchand@yahoo.com)
# Created:     15/03/2013
# ------------------------------------------------------------------------------

import os
import sys
import getpass
from lxml import etree
import datetime,time
import psycopg2
import dbconfig as config
from argparse import ArgumentParser
sys.path.append(r'/home/crowdtod/Projects/primDB/primdb')
os.environ['DJANGO_SETTINGS_MODULE'] = 'primdb.settings'
from django.db import models
from primdb_app.models import Searchspectrum_Query


TAGLIST=['mzML','sourceFile','software','dataProcessing','instrumentConfiguration','selectedIon']
NAMESPACE="{http://psi.hupo.org/ms/mzml}"


def fast_iter(context, func,*args,**kwargs):
    # fast_iter is useful if we need to free memory while iterating through a
    # very large XML file.
    #http://www.ibm.com/developerworks/xml/library/x-hiperfparse/

    # Author: Liza Daly

    for event, elem in context:
        func(elem,*args, **kwargs)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

def process_element(element):
    # Processing first element (mzML) and it's attributes (id, version, accession)
    # version attribute is required AND id & accession are optional
    if element.tag==NAMESPACE+TAGLIST[0]:
        # get mzml element id, accession and version attributes
        mzmlID = element.attrib.get('id','-')
        mzml_accession = element.attrib.get('accession','-')
        mzml_version = element.attrib.get('version','-')
        exp_id_fk = exp_PK

        # insert record into the database
        sql = "INSERT INTO primdb_app_mzml (mzml_id,accession,version,exp_id) VALUES (%s, %s, %s, %s) RETURNING id;"
        # Execute the SQL command
        config.cursor.execute(sql,(mzmlID,mzml_accession,mzml_version,exp_id_fk))
        global mzml_pk
        mzml_pk = config.cursor.fetchone()[0]

    # Processing second element (sourceFile) which has attributes (id, name and location)
    # SourceFile attributes id, name and location are required
    # Further, sourceFile has child element (cvParam) and attributes (cvRef, name, accession, value)
    # cvParam attributes: cvRef, name, accession are Required and value optional

    elif element.tag==NAMESPACE+TAGLIST[1]:
        sf_id = element.attrib.get('id','-')
        sf_name = element.attrib.get('name','-')
        sf_location = element.attrib.get('location','-')
        global sf_fk
        sf_fk = mzml_pk
    
        # insert sourceFile record into the database

        sql = "INSERT INTO primdb_app_source_file  (sf_id,name,location,mzml_fk_id) VALUES (%s, %s, %s, %s) RETURNING id;"
        # Execute the SQL command
        config.cursor.execute(sql,(sf_id,sf_name,sf_location,sf_fk))
        global sf_cv_fk
        sf_cv_fk= config.cursor.fetchone()[0]
        
        for child in element.getchildren():
            sf_cv_name = child.attrib.get('name', '-')
            sf_cv_accession = child.attrib.get('accession','-')
            sf_cv_value = child.attrib.get('value','-')
            
            # insert sourceFile CV record into the database
            sql = "INSERT INTO primdb_app_source_file_cv (accession,name,value,sf_fk_id) VALUES (%s, %s, %s, %s)"
            # Execute the SQL command
            config.cursor.execute(sql,(sf_cv_accession,sf_cv_name,sf_cv_value,sf_cv_fk))


    # Processing third element (software) attributes and it's child element (cvParam) attributes
    # software attribute id is Required and version is optional
    # Further, software have child element (cvParam) and attributes (cvRef, accession, name, value)
    # cvParam attributes: cvRef, accession, name are Required and value optional

    elif element.tag==NAMESPACE+TAGLIST[2]:
        softw_id = element.attrib.get('version','-')
        softw_version = element.attrib.get('id','-')
        softw_fk_ID = mzml_pk

        #Insert Software record into the database
        sql = "INSERT INTO primdb_app_software (soft_id,version,soft_fk_id) VALUES (%s, %s, %s) RETURNING id;"
        # Execute the SQL command
        config.cursor.execute(sql,(softw_id,softw_version,softw_fk_ID))

        for child in element.getchildren():
            
            soft_cv_accession = child.attrib.get('accession','-')
            soft_cv_name = child.attrib.get('name','-')
            soft_cv_value = child.attrib.get('value','-')
            global softw_cv_fk_ID
            softw_cv_fk_ID = config.cursor.fetchone()[0]

            # Insert Software_cv record into the database
            sql = """INSERT INTO primdb_app_software_cv (accession,name, value,soft_cv_fk_id)
                    VALUES (%s, %s, %s, %s)"""
           # Execute the SQL command
            config.cursor.execute(sql,(soft_cv_accession,soft_cv_name,soft_cv_value,softw_cv_fk_ID))

    # Processing fourth element (dataProcessing) attributes
    # dataProcessing element attribute id is Required
    # Further, dataProcessing has child element (processingMethod) and attribute (softwareRef) required
    # processingMethod have child element(cvParam)
    # cvParam element have attributes (cvRef,accession, name) required and name & value optional

    elif element.tag==NAMESPACE+TAGLIST[3]:
        data_id = element.attrib.get('id','-')
        global data_mzml_pk_id
        data_mzml_pk_id = mzml_pk
        # Insert dataProcessor record into the database
        sql = """INSERT INTO primdb_app_dataprocessing (dp_id,data_fk_id)
        VALUES (%s, %s) RETURNING id;"""
        # Execute the SQL command
        config.cursor.execute(sql,(data_id, data_mzml_pk_id))

        global data_pk_id
        data_pk_id = config.cursor.fetchone()[0]

        for child in element.getchildren():
            dataP_softRef = child.attrib.get('softwareRef','-')

            # Insert the dataProcessor tool record into the database
            sql = """INSERT INTO primdb_app_data_pro_method (p_soft_ref,data_p_fk_id)
            VALUES (%s, %s) RETURNING id;"""
            # Execute the SQL command
            config.cursor.execute(sql,(dataP_softRef, data_pk_id))

            global data_pro_pk_id
            data_pro_pk_id= config.cursor.fetchone()[0]
            for grandchild in child.getchildren():

                data_cv_accession = grandchild.attrib.get('accession','-')
                data_cv_name = grandchild.attrib.get('name','-')
                data_cv_value = grandchild.attrib.get('value','-')
                # Insert dataProcessor CV record into the database
                sql = """INSERT INTO primdb_app_data_pro_cv (accession,name,value,pro_meth_fk_id)
                        VALUES (%s, %s, %s, %s)"""
                # Execute the SQL command
                config.cursor.execute(sql,(data_cv_accession,data_cv_name,data_cv_value,data_pro_pk_id))

    # Processing fifth element (instrumentConfiguration) attributes
    # instrumentConfiguration element attribute id is Required
    # Further, instrumentConfiguration have childs ionsource, analyzer and detector under cvParam element
    # cvParam element have attributes (cvRef,accession, name) required and name & value optional
    elif element.tag==NAMESPACE+TAGLIST[4]:
        global inspro_fk
        inspro_fk = mzml_pk
        inspro_id = element.attrib['id']

        # Insert Instrument ID record into the database
        sql = """INSERT INTO primdb_app_instrumentconfiguration (ins_id, ins_pro_fk_id)
        VALUES (%s, %s) RETURNING id;"""
        # Execute the SQL command
        config.cursor.execute(sql,(inspro_id,inspro_fk))

        global inspro_pk_id
        inspro_pk_id = config.cursor.fetchone()[0]

        # Three tag list of the instrumentConfiguration element: source, analyzer and detector
        child_need = ['{http://psi.hupo.org/ms/mzml}source','{http://psi.hupo.org/ms/mzml}analyzer','{http://psi.hupo.org/ms/mzml}detector']
        for child in element.getchildren()[1]:
            # get all the attributes of the first child (ionsource) of the
            # instrumentConfiguration Element 
            if child_need[0] in child.tag:
                for grandchild in child.getchildren():
                    source_cv_accession = grandchild.attrib.get('accession','-')
                    source_cv_name = grandchild.attrib.get('name','-')
                    source_cv_value = grandchild.attrib.get('value','-')

                    # Insert ionSource record into the database
                    sql = """INSERT INTO primdb_app_insconsource (accession,name,value,inss_fk_id_id)
                    VALUES (%s, %s, %s, %s)"""
                    # Execute SQL command
                    config.cursor.execute(sql,(source_cv_accession, source_cv_name, source_cv_value, inspro_pk_id))

            # get all the attributes of the second child (ionanalayzer) of the
            # instrumentConfiguration Element 
            if child_need[1] in child.tag:
                for grandchild in child.iterchildren():
                    analyzer_cv_accession = grandchild.attrib.get('accession','-')
                    analyzer_cv_name = grandchild.attrib.get('name','-')
                    analyzer_cv_value = grandchild.attrib.get('value','-')

                    # Insert ionanalyzer record into the database
                    sql = """INSERT INTO primdb_app_insconanalyzer (accession,name,value,insa_fk_id_id)
                    VALUES (%s, %s, %s, %s)"""
                    # Execute the SQL command
                    config.cursor.execute(sql,(analyzer_cv_accession, analyzer_cv_name, analyzer_cv_value, inspro_pk_id))

             # get all the attributes of the third child (iondetector) of the
            # instrumentConfiguration Element
            if child_need[2] in child.tag:
                for grandchild in child.getchildren():
                    detector_cv_accession = grandchild.attrib.get('accession','-')
                    detector_cv_name = grandchild.attrib.get('name','-')
                    detector_cv_value = grandchild.attrib.get('value','-')

                    # Insert iondetector record into the database
                    sql = """INSERT INTO primdb_app_inscondetector (accession,name,value,insd_fk_id_id)
                    VALUES (%s, %s, %s, %s)"""
                    # Execute the SQL command
                    config.cursor.execute(sql,(detector_cv_accession, detector_cv_name, detector_cv_value, inspro_pk_id))


    #SelectedIon
    elif element.tag==NAMESPACE+TAGLIST[5]:
        global sele_fk
        sele_fk = mzml_pk
        for sele_child in element.getchildren():
            #selectedIon element child element attribute name with selected ion m/z value
            #and subelement attribute name charge state with value
            if sele_child.attrib['name']=="selected ion m/z":
                monoiso = sele_child.attrib['value']
            if sele_child.attrib['name']=='charge state':
                charges =  sele_child.attrib['value']
            if sele_child.attrib['name']=='peak intensity':
                peakinten =  sele_child.attrib['value']

                # Insert selected precursor mass record into the database
                sql = """INSERT INTO primdb_app_selectedion (monoiso, chargestate,peakinten, sele_fk_id)
                    VALUES (%s, %s, %s, %s) RETURNING id;"""

                # Execute the SQL command
                config.cursor.execute(sql,(monoiso, charges,peakinten, sele_fk))
                global sele_pk
                sele_pk = config.cursor.fetchone()[0]

        spect=NAMESPACE+'spectrum'
        for ancestor in sele_child.iterancestors(spect):
            spect_id = ancestor.attrib['id']
            spect_index =  ancestor.attrib['index']
            spect_defaultarraylength = ancestor.attrib['defaultArrayLength']
            expname = filename_GV
            spectrum_id = int(spect_index) + 1
            result = Searchspectrum_Query.objects.filter(spec_query_fk__filename=expname) \
                        .filter(spectrum=spectrum_id)
            if result:
                identified = "Y"
            else:
                identified = "N"
            # Insert the selectedion spectra record into the database
            sql = """INSERT INTO primdb_app_spectrum (spec_id, spec_index, spec_defaultarraylength, identified, spec_fk_id)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id;"""
            # Execute the SQL command
            config.cursor.execute(sql,(spect_id,spect_index, spect_defaultarraylength, identified, sele_pk))
            global spec_pk
            spec_pk = config.cursor.fetchone()[0]
            specvParam=NAMESPACE+'cvParam'
            # Spectrum cvParam attribute cvRef, accession, name and value
            # In database it will be store in Spectrum_cv table

            for specancestor in ancestor.iterchildren(specvParam):
                spec_cv_accession = specancestor.attrib.get('accession','-')
                spec_cv_name = specancestor.attrib.get('name','-')
                spec_cv_value = specancestor.attrib.get('value','-')

                # Insert Spectrum CV record into the database
                sql = """INSERT INTO primdb_app_spectrum_cv (accession,name,value,spec_cv_fk_id)
                        VALUES (%s, %s, %s, %s)"""
                try:
                    # Execute the SQL command
                    config.cursor.execute(sql,(spec_cv_accession,spec_cv_name,spec_cv_value,spec_pk))
                    # Commit your changes in the database
                    config.conn.commit()
                except Exception as err:
                    # logger.error(err)
                    # Rollback in case there is any error
                    config.conn.rollback()
        # Scan list
        scan = ancestor.find(".//"+NAMESPACE+"scan")
        for cvparam in scan.getchildren():
            if cvparam.tag==NAMESPACE+'cvParam':
                sname = cvparam.attrib.get('name','-')
                svalue = cvparam.attrib.get('value','-')
                saccession = cvparam.attrib.get('accession','')
            if cvparam.tag==NAMESPACE+'userParam':
                sname = cvparam.attrib.get('name','-')
                svalue = cvparam.attrib.get('value','-')
                saccession = '-'
            try:
                # Insert the spectra scan list CV record into the database
                sql = """INSERT INTO primdb_app_scan (accession,name,value,scan_fk_id)
                                    VALUES (%s, %s, %s, %s)"""
                config.cursor.execute(sql,(saccession,sname,svalue,spec_pk))
                config.conn.commit()
            except:
                config.conn.rollback()

        #Scan Window
        scanw = ancestor.find(".//"+NAMESPACE+"scanWindow")
        for cvparam in scanw.getchildren():
            if cvparam.tag==NAMESPACE+'cvParam':
                waccession = cvparam.attrib.get('accession','-')
                wname = cvparam.attrib.get('name','-')
                wvalue = cvparam.attrib.get('value','-')

            try:
                # Insert the scan window record of scan list into the database
                sql = """INSERT INTO primdb_app_scanwindow (accession,name,value,scanw_fk_id)
                         VALUES (%s, %s, %s, %s)"""
                # Execute the SQL command
                config.cursor.execute(sql,(waccession,wname,wvalue,spec_pk ))
                config.conn.commit()
            except Exception as err:
                #logger.error(err)
                # Rollback in case there is any error
                config.conn.rollback()


def convert_bytes(bytes):
    '''
    return the size of the file
    '''
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fTB' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fGB' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fKB' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size


def file_exist(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def main():
    stime = time.time()
    parser = ArgumentParser(description="mzML parse")
    parser.add_argument("-f", "--input", dest="filename", required=True,
                    help="provide mzML file name",
                    metavar="FILE", type=lambda x: file_exist(parser,x))
    # file from the argument
    args = parser.parse_args()
    mzml_file = args.filename
    dir_and_filename = [os.getcwd(), mzml_file]  # list of current dir and file
    file_dir = '/'.join(dir_and_filename)
    try:
        config.cursor.execute("SELECT * FROM primdb_app_pepxml WHERE filename=filename")
        if config.cursor.fetchone():
            # The basic properties of the file such as name, user, created date & time and size
            # The uploaded date and time which is current system date and time
            get_file = os.path.basename(file_dir) # extracting the current file in the directory path
            (name, ext) = os.path.splitext(get_file)    # File name and extension
            owner= str(getpass.getuser())    # the file owner
            file_name = name    # the name of the file 
            #file_created = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(file_dir)))
            file_uploaded = str(datetime.datetime.now().strftime("%d/%m/%Y"))
            file_size = convert_bytes(os.path.getsize(file_dir))
            source = file_dir # the file source/full path

            # Insert file properties data into the table primdb_app_experiment
            #sql_string = "INSERT INTO primdb_app_experiment VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
            # Execute the SQL command
            #config.cursor.execute(sql_string, (owner,file_name, file_created, file_uploaded, file_size, source))
            sql_string = "INSERT INTO primdb_app_experiment (fileuser,filename,uploaddate, size, located) VALUES (%s,%s,%s,%s,%s) RETURNING id;"
            config.cursor.execute(sql_string, (owner,file_name, file_uploaded, file_size, source))
            global exp_PK, filename_GV # global variables
            exp_PK, filename_GV = config.cursor.fetchone()[0], file_name

            # Reading elements from file
            for tag in TAGLIST:
                context= etree.iterparse(file_dir,events=("end",),tag=NAMESPACE+tag, huge_tree=True, remove_blank_text=True)
                fast_iter(context, process_element)

        else:
            print "Please upload pepXML file before mzML"

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

    finally:
        if config.conn:
            config.conn.close()
            print "Time of execution: %.3f" % (time.time() - stime) + "seconds"
            config.conn.close()

if __name__ == '__main__':
    main()