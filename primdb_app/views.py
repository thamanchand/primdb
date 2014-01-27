# Create your views here.
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.context import RequestContext
from models import *
from itertools import chain
from collections import defaultdict


def mzml(request):
    allexp = Experiment.objects.all()
    paginator = Paginator(allexp, 1)  # show 10 mzml per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render_to_response('mzml.html', {"exp": contacts},
                                context_instance=RequestContext(request))


def pepxml(request):
    allpepxml = pepXML.objects.all()
    paginator = Paginator(allpepxml, 1)  # show 10 mzml per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render_to_response('pepxml.html', {"pepxml": contacts},
                                context_instance=RequestContext(request))


def index(request):
    expcount = Experiment.objects.count()
    allmass = SelectedIon.objects.count()
    allpep = pepXML.objects.count()
    lastexp = Experiment.objects.latest('id')
    #lastpep = pepXML.objects.latest('id')
    #cid = request.POST['cnum']
    #fid = request.FILES['myfile']
    errors = []

    """
    1) check whether post is from input text and it's not blank.
    2) get all forms request values mz, searchdate, search space, charge state
    and ppm.
    3) if charge state is none (default) then calculate lower range and upper
    ppm range.
    4) if charge state is provided in the request then protonated it by
    multiplying with 1.00727638 and caculate lower and upper ppm mass range.
    """
    if 'textmz' in request.POST and request.POST['textmz'] != '' and \
    'myfile' not in request.FILES:
        cid = request.POST['textmz']
        searchdate = request.POST['fdate1']
        sspace = request.POST['r']
        cstate = request.POST['ch']
        ppm = request.POST.__getitem__('ppm')

        if request.POST['ch'] == 'none':
            defmass = float(ppm) / int(1000000)
            massvalue = float(cid)
            masscon = defmass * massvalue
            highrange = massvalue + masscon
            lowrange = massvalue - masscon
            prec = request.POST['prec']
        elif request.POST['ch'] == 'neutral':
            prec = request.POST['prec']
            masscon, mass_with_charges = [], []

            for charge in range(1, 6):
                mass_with_charges.append((float(cid) + (charge * 1.00727638)) / charge)
            defmass = float(5) / int(1000000)
            [masscon.append(defmass * item) for item in mass_with_charges]
            upper_mass_range = [sum(pair) for pair in zip(mass_with_charges, masscon)]
            lower_mass_range = [a - b for a, b in zip(mass_with_charges, masscon)]
        else:
            defmass = float(ppm) / 1000000
            charge = int(cstate) * float(1.00727638)
            cm = float(cid)
            massvalue = (cm + charge) / int(cstate)
            masscon = defmass * massvalue
            highrange = massvalue + masscon
            lowrange = massvalue - masscon
            prec = request.POST['prec']
        # check all requests/input and perform query
        if searchdate == "" and sspace == 'all':
            if request.POST['ch'] == 'none':
                myquery = SelectedIon.objects.select_related(). \
                            filter(monoiso__range=(lowrange, highrange)). \
                            order_by('monoiso')
                querycount = myquery.count()
            elif request.POST['ch'] == 'neutral':
                myquery, queryresult = [], []
                for x, y in zip(lower_mass_range, upper_mass_range):
                    result = SelectedIon.objects.select_related() \
                                .filter(monoiso__range=(x, y)) \
                                .order_by('monoiso')
                    queryresult.append(result)
                # remove empty item list from the myquery list
                myquery = [x for x in queryresult if x]
                # make a flat list from a list of lists
                myquery = [item for sublist in myquery for item in sublist]
                querycount = len(myquery)
                myquerylist = list(myquery)
                chargecount, masses= [], []
                mass_with_charge = []
                for chargemass in myquerylist:
                    charge = str(chargemass.chargestate)
                    chargecount.append(chargemass.chargestate)
                    masses.append(chargemass.monoiso)
                    mass_with_charge.append([int(chargemass.chargestate), chargemass.monoiso],)
                #mass_dict = {{t[0]:t[1:],} for t in mass_with_charge}
                mass_dict = dict(mass_with_charge)
                d1 = defaultdict(list)
                for k, v in mass_with_charge:
                    d1[k].append(v)
                d = dict((k, tuple(v)) for k ,v in d1.iteritems())
                mytype = type(d)


            else:
                myquery = SelectedIon.objects.select_related() \
                            .filter(chargestate__iexact=cstate) \
                            .filter(monoiso__range=(lowrange, highrange)) \
                            .order_by('monoiso')
                querycount = myquery.count()

        elif searchdate and sspace == 'all':
            if request.POST['ch'] == 'none':
                myquery = SelectedIon.objects.select_related() \
                            .filter(monoiso__range=(lowrange, highrange)) \
                            .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                            .order_by('monoiso')
                querycount = myquery.count()
            else:
                myquery = SelectedIon.objects.select_related() \
                            .filter(chargestate__iexact=cstate) \
                            .filter(monoiso__range=(lowrange, highrange)) \
                            .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                            .order_by('monoiso')
                querycount = myquery.count()
        elif searchdate and sspace == 'recent':
            if request.POST['ch'] == 'none':
                myquery1 = SelectedIon.objects.select_related() \
                            .filter(monoiso__range=(lowrange, highrange)) \
                            .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                            .reverse()[:5]
                myquery = sorted(myquery1, key=lambda o: o.monoiso)
                querycount = sum(1 for result in myquery)
            else:
                myquery1 = SelectedIon.objects.select_related() \
                .filter(chargestate__iexact=cstate) \
                .filter(monoiso__range=(lowrange, highrange)) \
                .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                .reverse()[:5]
                myquery = sorted(myquery1, key=lambda o: o.monoiso)
                querycount = sum(1 for result in myquery)

        elif searchdate == "" and sspace == 'recent':
            if request.POST['ch'] == 'none':
                myquery1 = SelectedIon.objects.select_related() \
                            .filter(monoiso__range=(lowrange, highrange))[:5]
                myquery = sorted(myquery1, key=lambda o: o.monoiso)
                querycount = sum(1 for result in myquery)
            else:
                myquery1 = SelectedIon.objects.select_related() \
                            .filter(chargestate__iexact=cstate) \
                            .filter(monoiso__range=(lowrange, highrange))[:5]
                myquery = sorted(myquery1, key=lambda o: o.monoiso)
                querycount = sum(1 for result in myquery)
        if myquery:
            template = 'result.html'
            #'high': highrange,'low': lowrange,'qcount': querycount,
            #'masses': masses,'mass_with_charge': mass_with_charge,
            #'mass_dict':mass_dict,
            #'dict':d, 'mytype': mytype
            return render_to_response(template, {'prec': prec, 'query': cid,
                                                'sections': myquery, 'qcount': querycount,
                                                'cs': cstate, 'ppm': ppm,
                                                'defm': defmass, 'ss': sspace,
                                                'sd': searchdate, 
                                                },
                                                context_instance=RequestContext(request))
        else:
            errors.append("*Didn't match with any precursor ion mass in database!!")
            #'pep': lastpep,
            return render_to_response('index.html', {'exp': expcount,
                                        'mass': allmass, 'latest': lastexp, 'pep': allpep,
                                        'errmsg': errors, 
                                         },
                                        context_instance=RequestContext(request))
    # check whether post is from UPLOAD FILE and TEXT input is blank.
    # get all forms request values mz, searchdate, search space, charge state
    # and ppm.
    # if charge state is none (default) then calculate lower range and upper
    # ppm range.
    # if charge state is provided in the request then protonate it by multiplying
    # with 1.00727638 and caculate lower and upper ppm mass range
    elif 'myfile' in request.FILES and request.POST['textmz'] == '':
        searchdate = request.POST['fdate1']
        sspace = request.POST['r']
        cstate = request.POST['ch']
        ppm = request.POST.__getitem__('ppm')
        prec = request.POST['prec']
        mfile = request.FILES['myfile']
        # split file name and check if extension is txt
        if mfile.name.split('.')[1] == "txt":
            if request.POST['ch'] == 'none':
                fileid = []
                searchid = []
                masscon = []
                defmass = float(ppm) / int(1000000)
                fread = mfile.readlines()
                [searchid.append(float(item)) for item in fread]
                [fileid.append(float(item)) for item in fread]
                [masscon.append(defmass * item) for item in fileid]
                newlist = [sum(pair) for pair in zip(fileid, masscon)]
                newlist1 = [a - b for a, b in zip(fileid, masscon)]
                #newlist2 = [[x, y] for x, y in zip(newlist, newlist1)]
            else:
                defmass = float(ppm) / int(1000000)
                charge = int(cstate) * float(1.00727638)
                prec = request.POST['prec']
                fileid = []
                searchid = []
                masscon = []
                defmass = float(ppm) / int(1000000)
                fread = mfile.readlines()
                [searchid.append(float(item)) for item in fread]
                [fileid.append(float(item)) for item in fread]
                [masscon.append(defmass * item) for item in fileid]
                newlist = [sum(pair) for pair in zip(fileid, masscon)]
                newlist1 = [a - b for a, b in zip(fileid, masscon)]
                #newlist2 = [[x, y] for x, y in zip(newlist, newlist1)]

            if searchdate == "" and sspace == 'all':
                if request.POST['ch'] == 'none':
                    myresult = []
                    for x, y in zip(newlist1, newlist):
                        myquery = SelectedIon.objects.select_related() \
                                    .filter(monoiso__range=(x, y)) \
                                    .order_by('monoiso')
                        myresult.append(myquery)
                else:
                    myresult = []
                    for x, y in zip(newlist1, newlist):
                        myquery = SelectedIon.objects.select_related() \
                                    .filter(chargestate__iexact=cstate) \
                                    .filter(monoiso__range=(x, y)) \
                                    .order_by('monoiso')
                        myresult.append(myquery)
            elif searchdate and sspace == 'all':
                myresult = []
                if request.POST['ch'] == 'none':
                    for x, y in zip(newlist1, newlist):
                        myquery = SelectedIon.objects.select_related() \
                                    .filter(monoiso__range=(x, y)) \
                                    .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                                    .order_by('monoiso')
                        myresult.append(myquery)
                else:
                    for x, y in zip(newlist1, newlist):
                        myquery = SelectedIon.objects.select_related() \
                        .filter(chargestate__iexact=cstate) \
                        .filter(monoiso__range=(x, y)) \
                        .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                        .order_by('monoiso')
                        # end of queryset
                        myresult.append(myquery)
            elif searchdate and sspace == 'recent':
                myresult = []
                if request.POST['ch'] == 'none':
                    for x, y in zip(newlist1, newlist):
                        myquery1 = SelectedIon.objects.select_related() \
                                    .filter(monoiso__range=(x, y)) \
                                    .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                                    .reverse()[:5]
                        # end of queryset
                        myquery = sorted(myquery1, key=lambda o: o.monoiso)
                        myresult.append(myquery)
                else:
                    for x, y in zip(newlist1, newlist):
                        myquery1 = SelectedIon.objects.select_related(). \
                                    filter(chargestate__iexact=cstate). \
                                    filter(monoiso__range=(x, y)) \
                                    .filter(sele_fk__exp__uploaddate__iexact=searchdate) \
                                    .reverse()[:5]
                        # end of queryset
                        myquery = sorted(myquery1, key=lambda o: o.monoiso)
                        myresult.append(myquery)
            elif searchdate == "" and sspace == 'recent':
                myresult = []
                if request.POST['ch'] == 'none':
                    for x, y in zip(newlist1, newlist):
                        myquery1 = SelectedIon.objects.select_related(). \
                                    filter(monoiso__range=(x, y))[:5]
                        # end of queryset
                        myquery = sorted(myquery1, key=lambda o: o.monoiso)
                        myresult.append(myquery)
                else:
                    for x, y in zip(newlist1, newlist):
                        myquery1 = SelectedIon.objects.select_related() \
                                    .filter(chargestate__iexact=cstate) \
                                    .filter(monoiso__range=(x, y))[:5]
                        # end of queryset
                        myquery = sorted(myquery1, key=lambda o: o.monoiso)
                        myresult.append(myquery)

            # count the length of the myresult queryset list
            querycount = len([num for elem in myresult for num in elem])
            if querycount > 1:
                template = 'result.html'
                return render_to_response(template, {'prec': prec,
                                                    'filesection': myresult,
                                                    'qcount': querycount,
                                                    'range': range(1, (querycount + 1)),
                                                    'cs': cstate, 'ppm': ppm,
                                                    'ss': sspace, 'sd': searchdate,
                                                    'file': mfile,
                                                    'search_id': searchid,
                                                    'fileid': fileid, },
                                                    context_instance=RequestContext(request))
            else:
                errors.append("*Didn't match with any precursor ion masses in database!!!!")
                return render_to_response('index.html', {'exp': expcount,
                                        'mass': allmass, 'latest': lastexp, 'pep': allpep,
                                        'errmsg': errors,
                                         },
                                        context_instance=RequestContext(request))
        else:
            errors.append("*Only text file is suppored!!")
            return render_to_response('index.html', {'exp': expcount, 'mass': allmass, 
                                                    'latest': lastexp, 'pep': allpep,
                                                    'errmsg': errors,
                                                    },
                                                     context_instance=RequestContext(request))

    elif 'myfile' in request.FILES and 'textmz' in request.POST:
        errors.append("*Search doesn't accept multiple inputs!!!")
        return render_to_response('index.html', {'exp': expcount, 'mass': allmass, 'pep': allpep,
                                                'latest': lastexp, 'errmsg': errors,
                                                 },
                                                context_instance=RequestContext(request))

    elif ('textmz' in request.POST and request.POST['textmz'] == '') \
        or ('myfile' in request.FILES and request.FILES['myfile'] == ''):
        errors.append("*Search requires one input!!!")
        #'pep': allpep,
        return render_to_response('index.html', {'exp': expcount, 'mass': allmass,
                                                'latest': lastexp, 'errmsg': errors,
                                                 'pep': allpep,},
                                                context_instance=RequestContext(request))

    else:
    	#'pep': allpep,
        return render_to_response('index.html', {'exp': expcount, 'mass': allmass,
                                            'latest': lastexp, 
                                            'user': request.user, 'pep': allpep,},
                                             context_instance=RequestContext(request))


def detail(request, match, tab):
    if request.is_ajax():
        spect = Spectrum.objects.filter(spec_fk__id__iexact=match).select_related()
        spect_cv = Spectrum_CV.objects.filter(spec_cv_fk__spec_fk__id__iexact=match)
        scanwin = ScanWindow.objects.filter(scanw_fk__spec_fk__id__iexact=match)
        scan = Scan.objects.filter(scan_fk__spec_fk__id__iexact=match)
        expfile = SelectedIon.objects.get(id=match)
        expname = expfile.sele_fk.exp.filename
        scanlist = list(scan)
        template = 'default.html'
        return render_to_response(template, {'spect': spect, 'spect_cv': spect_cv,
                                            'expname': expname, 'scanw': scanwin,
                                            'scan': scan,'scanlist':scanlist, },
                                            context_instance=RequestContext(request))


def matchdetail(request, match_id, tab_id):
    if request.is_ajax():
        spect = Spectrum.objects.filter(spec_fk__id__iexact=match_id).select_related()
        spect_cv = Spectrum_CV.objects.filter(spec_cv_fk__spec_fk__id__iexact=match_id)
        scanwin = ScanWindow.objects.filter(scanw_fk__spec_fk__id__iexact=match_id)
        scan = Scan.objects.filter(scan_fk__spec_fk__id__iexact=match_id)
        expfile = SelectedIon.objects.get(id=match_id)
        expname = expfile.sele_fk.exp.filename
        scanlist = list(scan)
        # spectid = Spectrum.objects.get(spec_fk__id__iexact=match_id)
        # searchspect_id = spectid.spec_index + 1
        template = 'tab1.html'
        return render_to_response(template, {'spect': spect, 'spect_cv': spect_cv,
                                            'expname': expname, 'scanw': scanwin,
                                            'scan': scan, 'scanlist':scanlist,},
                                            context_instance=RequestContext(request))


def tabdetail(request, tab_id, match_id):
    if request.is_ajax():
        tabvalue = tab_id
        if tabvalue == '1':
            spect = Spectrum.objects.filter(spec_fk__id__iexact=match_id).select_related()
            spect_cv = Spectrum_CV.objects.filter(spec_cv_fk__spec_fk__id__iexact=match_id)
            scanwin = ScanWindow.objects.filter(scanw_fk__spec_fk__id__iexact=match_id)
            scan = Scan.objects.filter(scan_fk__spec_fk__id__iexact=match_id).values()
            scanlist = list(scan)

            template = 'tab1.html'
            return render_to_response(template, {
                                                'scanlist': scanlist, 'spect': spect, 'spect_cv': spect_cv,
                                                'scan': scan, 'scanw': scanwin,},
                                                context_instance=RequestContext(request))
        # end of tab 1
        elif tabvalue == '2':
            spect = Spectrum.objects.get(spec_fk__id__iexact=match_id)
            searchspect_id = spect.spec_index + 1
            expfile = SelectedIon.objects.get(id=match_id)
            expname = expfile.sele_fk.exp.filename
            result = Searchspectrum_Query.objects.filter(spec_query_fk__filename=expname) \
                        .filter(spectrum=searchspect_id)
            # end of queryset
            for i in result:
                spect_id = i.id
            pepsearch = Search_Hit.objects \
                        .filter(search_hit_fk__spec_query_fk__filename=expname) \
                        .filter(search_hit_fk__spectrum=searchspect_id).order_by('hit_rank')
            # end of queryset
            if pepsearch:
                altp = Alternative_Protein.objects \
                        .filter(altpro_fk__spec_query_fk__filename=expname) \
                        .filter(altpro_fk=spect_id)
                # end of queryset
                template = 'tab2.html'
                return render_to_response(template, {'spectquery': result,
                                                    'pepsearch': pepsearch,
                                                    'alt_p': altp, 'spect': spect, },
                                                     context_instance=RequestContext(request))
            else:
                template = 'tab2.html'
                return render_to_response(template, {'error': 'No match found', },
                                        context_instance=RequestContext(request))
        # end of tab 2
        elif tabvalue == '4':
            data = SelectedIon.objects.filter(id=match_id)
            mzml_query = SelectedIon.objects.get(id=match_id)
            mzml_id = str(mzml_query.sele_fk.id)
            sf = Source_File.objects.filter(mzml_fk__id__iexact=mzml_id)
            source = Source_file_CV.objects.filter(sf_fk__id__iexact=mzml_id)
            soft = Software.objects.filter(soft_fk__id__iexact=mzml_id)
            result_list = list(chain(sf, source))
            software = Software_CV.objects.filter(soft_cv_fk__id__iexact=mzml_id).select_related()
            datap = DataProcessing.objects.filter(data_fk__id__iexact=mzml_id)
            data_p = Data_Pro_CV.objects.filter(pro_meth_fk__data_p_fk__data_fk__id__iexact=mzml_id).select_related()
            inss = InsConSource.objects.filter(inss_fk_id__id__iexact=mzml_id)
            insa = InsConAnalyzer.objects.filter(insa_fk_id__id__iexact=mzml_id)
            insd = InsConDetector.objects.filter(insd_fk_id__id__iexact=mzml_id)
            insid = InstrumentConfiguration.objects.filter(ins_pro_fk__id__iexact=mzml_id)
            instru_list = list(chain(inss, insa, insd))
            template = 'tab4.html'
            return render_to_response(template, {'instrument_list': instru_list,
                                                'ins_id': insid, 'results': data,
                                                'source': result_list, 'sf': sf,
                                                'scv': source, 'software': software,
                                                'datap': datap, 'datapro': data_p,
                                                'inss': inss, 'insa': insa,
                                                'insd': insd, 'soft': soft, },
                                                context_instance=RequestContext(request))
        # end of tab 4
        else:
            spect = Spectrum.objects.get(spec_fk__id__iexact=match_id)
            searchspect_id = spect.spec_index + 1
            expfile = SelectedIon.objects.get(id=match_id)
            expname = expfile.sele_fk.exp.filename
            result = Searchspectrum_Query.objects.filter(spec_query_fk__filename=expname).filter(spectrum=searchspect_id)
            for i in result:
                spect_id = i.id
            setting = Search_Setting.objects.filter(search_fk__filename=expname)
            template = 'tab5.html'
            return render_to_response(template, {'ssetting': setting, },
                                        context_instance=RequestContext(request))