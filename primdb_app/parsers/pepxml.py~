#!/usr/local/bin/python
# ------------------------------------------------------------------------------
# Name:         pepXML parser
# Purpose:      Parser for MS-based Proteomics pepXML file, parses the selected
#               pepXML elements information into the database.
# Author:      Thaman Chand (thamanchand@yahoo.com)
# Created:     15/03/2013
# ------------------------------------------------------------------------------


import os
import getpass
from lxml import etree
import datetime
import time
from argparse import ArgumentParser
import dbconfig as config

NAMESPACE = '{http://regis-web.systemsbiology.net/pepXML}'
TAGLIST = ['spectrum_query', 'search_result']


def fast_iter(context, func, *args, **kwargs):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    for event, elem in context:
        func(elem, *args, **kwargs)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def process_element(elt):
    if elt.tag == NAMESPACE + "spectrum_query" and elt.getchildren():
        #print "\n"
        #print "###### SPECTRUM QUERY ##### \n"
        spect_id = (elt.attrib.get('spectrum', '-').split(' ')[1][0:-1]).split(':')[1]
        pnm = elt.attrib.get('precursor_neutral_mass', '-')
        assumecharge = elt.attrib.get('assumed_charge', '-')

        pepxml_id = pep_PK

        try:
            sql = "INSERT INTO primdb_app_searchspectrum_query (spectrum,pre_neu_mass,assume_charge,spec_query_fk_id) VALUES (%s, %s, %s, %s) RETURNING id;"
            config.cursor.execute(sql, (spect_id, pnm, assumecharge, pepxml_id))
            config.conn.commit()
        except Exception as err:
            # Rollback in case there is any error
            config.conn.rollback()

        SEARCH_PK_ID = config.cursor.fetchone()[0]

        child_need = ['{http://regis-web.systemsbiology.net/pepXML}search_result',
                    '{http://regis-web.systemsbiology.net/pepXML}search_hit',
                    '{http://regis-web.systemsbiology.net/pepXML}alternative_protein']

        for child in elt.getchildren()[0]:
            # Search_hit
            if child_need[1] in child.tag:
                #print "\n"
                #print "###### HIT_RANK ##### \n"
                hrank = child.attrib.get('hit_rank', '-')
                peptide = child.attrib.get('peptide', '-')
                previous_aa = child.attrib.get('peptide_prev_aa', '-')
                next_aa = child.attrib.get('peptide_next_aa', '-')
                protein = child.attrib.get('protein', '-')
                ntp = child.attrib.get('num_tot_proteins', '-')
                nmi = child.attrib.get('num_matched_ions', '-')
                cnpm = child.attrib.get('calc_neutral_pep_mass', '-')
                massdif = child.attrib.get('massdiff', '-')
                nmc = child.attrib.get('num_missed_cleavages', '-')
                pdesc = child.attrib.get('protein_descr', '-')

                try:
                    sql = """INSERT INTO primdb_app_search_hit (hit_rank,peptide,pep_prev_aa, pep_next_aa, protein,num_total_protein,num_matched_ions,calc_neutral_pep_mass,massdiff,num_missed_cleavage,protein_desc,search_hit_fk_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""
                    # Execute the SQL command
                    config.cursor.execute(sql,(hrank,peptide,previous_aa,next_aa,protein,ntp,nmi, cnpm,massdif,nmc,pdesc,SEARCH_PK_ID))
                    config.conn.commit()
                except Exception as err:
                    # Rollback in case there is any error
                    config.conn.rollback()

                global hit_PK
                hit_PK = config.cursor.fetchone()[0]
                for grandchild in child.getchildren():
                    if grandchild.tag == NAMESPACE+"alternative_protein":
                        #print "\n###### Alternative Protein  ##### \n"
                        alt_protein = grandchild.attrib.get('protein','-')
                        try:
                            sql = """INSERT INTO primdb_app_alternative_protein (protein,altpro_fk_id)
                                        VALUES (%s, %s)"""
                            # Execute the SQL command
                            config.cursor.execute(sql,(alt_protein,SEARCH_PK_ID))
                            config.conn.commit()
                        except Exception as err:
                            # Rollback in case there is any error
                            config.conn.rollback()
                    if grandchild.tag == NAMESPACE+"search_score":
                        #print "\n###### SCORE ##### \n"
                        if grandchild.attrib['name'] == "ionscore":
                            ions = grandchild.attrib.get('value','-')
                        if grandchild.attrib['name'] == "identityscore":
                            identitys = grandchild.attrib.get('value','-')
                        if grandchild.attrib['name'] == "homologyscore":
                            homologs = grandchild.attrib.get('value','-')
                        if grandchild.attrib['name'] == "expect":
                            expects = grandchild.attrib.get('value','-')

                        try:
                            sql = """INSERT INTO primdb_app_search_score (ionscore,identityscore,exceptscore,search_score_fk_id)
                                        VALUES (%s, %s, %s, %s)"""
                            # Execute the SQL command
                            config.cursor.execute(sql,(ions,identitys,expects,SEARCH_PK_ID))
                            config.conn.commit()
                        except Exception as err:
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
    parser = ArgumentParser(description="pepXML parse")
    parser.add_argument("-f", "--input", dest="filename", required=True,
                    help="provide pepxml file name",
                    metavar="FILE", type=lambda x: file_exist(parser,x))
    # file from the argument
    args = parser.parse_args()
    dir_and_filename = [os.getcwd(), args.filename]  # list of current dir and file
    file_dir = '/'.join(dir_and_filename)

    if file_dir:
        tree   = etree.parse(file_dir)
        seq = tree.find(".//"+NAMESPACE+"search_summary")
        setting = tree.findall(".//"+NAMESPACE+ "parameter")

        # file properties
        user= getpass.getuser()
        #pep_file_created_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(file_dir)))
        pep_file_uptime = str(datetime.datetime.now().strftime("%d/%m/%Y"))
        pep_file_size = convert_bytes(os.path.getsize(file_dir))
        basepath = seq.attrib['base_name']
        user_setting = []
        for item in setting:
            user_setting.append (item.get('value', '-'))

        # mascot settings
        pep_file_name = user_setting[1][0:-7]
        searchdatabase = user_setting[7]
        staxo = user_setting[18]
        smtype = user_setting[9]
        sfmodi = user_setting[8]
        svmodi = user_setting[17]
        senzyme = user_setting[10]
        smissclea = int(user_setting[6])
        spepchar = str(user_setting[22])
        sprtol = str(user_setting[2] + "ppm")
        siontol = str(user_setting[4] +"Da")
        sinstrument = str(user_setting[19])
        # insert into the pepxml table
        try:
            sql = """INSERT INTO primdb_app_pepxml (filename,fuser,uploaded,size,located,mascotpath)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"""
            config.cursor.execute(sql,(pep_file_name,user,pep_file_uptime,
                                    pep_file_size,file_dir,basepath))
            config.conn.commit()
        except Exception as err:
            # Rollback in case there is any error
            config.conn.rollback()
            print err

        global pep_PK
        pep_PK = config.cursor.fetchone()[0]
        # insert into the setting table
        try:
            sql = """INSERT INTO primdb_app_search_setting (mdatabase,mtaxonomy,
                                mmass,mfmodifi,mvmodifi,menzyme,maxmisscleav,
                                mpepcharge,mptol,mitol,minstrument,search_fk_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            # Execute the SQL command
            config.cursor.execute(sql,(searchdatabase,staxo,smtype,sfmodi,
                                svmodi,senzyme,smissclea,spepchar,sprtol,
                                siontol,sinstrument,pep_PK))
            config.conn.commit()
        except Exception as err:
            # Rollback in case there is any error
            config.conn.rollback()
            print err

        # parse the tree
        context = etree.iterparse(file_dir, events=('end',), tag=NAMESPACE+"spectrum_query")
        fast_iter(context, process_element)

        # close the connection
        config.conn.close()
        print "Time of execution: %.3f" % (time.time() - stime) + "seconds"
    else:
        print "Some error in locating files\n Usage: pepxml.py -f F012455.xml"


if __name__ == '__main__':
    main()

#import cProfile
#import pstats
#cProfile.run("main()")
