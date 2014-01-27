from django.db import models


#  The model for the pepXML
class pepXML(models.Model):
    filename = models.CharField(max_length=70, blank=False)
    fuser = models.CharField(max_length=60)
    uploaded = models.CharField(max_length=15)
    size = models.CharField(max_length=20)
    located = models.CharField(max_length=200)
    mascotpath = models.CharField(max_length=300)

    def __unicode__(self):
        return self.filename


class Searchspectrum_Query(models.Model):
    spectrum = models.CharField(max_length=150, null=True)
    pre_neu_mass = models.FloatField()
    assume_charge = models.IntegerField()
    spec_query_fk = models.ForeignKey(pepXML, null=True)

    def __unicode__(self):
        return self.spectrum


class Search_Hit(models.Model):
    hit_rank = models.IntegerField()
    peptide = models.CharField(max_length=100, blank=False)
    pep_prev_aa = models.CharField(max_length=2)
    pep_next_aa = models.CharField(max_length=2)
    protein = models.CharField(max_length=100)
    num_total_protein = models.IntegerField()
    num_matched_ions = models.IntegerField()
    calc_neutral_pep_mass = models.FloatField()
    massdiff = models.FloatField()
    num_missed_cleavage = models.IntegerField()
    protein_desc = models.CharField(max_length=200)
    search_hit_fk = models.ForeignKey(Searchspectrum_Query)

    def __unicode__(self):
        return self.peptide


class Alternative_Protein(models.Model):
    protein = models.CharField(max_length=100)
    altpro_fk = models.ForeignKey(Searchspectrum_Query)

    def __unicode__(self):
        return self.protein


class Search_Setting(models.Model):
    mdatabase = models.CharField(max_length=200)
    mtaxonomy = models.CharField(max_length=60)
    mmass = models.CharField(max_length=30)
    mfmodifi = models.CharField(max_length=120)
    mvmodifi = models.CharField(max_length=120)
    menzyme = models.CharField(max_length=15)
    maxmisscleav = models.IntegerField()
    mpepcharge = models.CharField(max_length=50)
    mptol = models.CharField(max_length=10)
    mitol = models.CharField(max_length=10)
    minstrument = models.CharField(max_length=50)
    search_fk = models.ForeignKey(pepXML)

    def __unicode__(self):
        return self.mdatabase, self.mmass


class Search_Score(models.Model):
    ionscore = models.CharField(max_length=10)
    identityscore = models.CharField(max_length=10)
    exceptscore = models.CharField(max_length=10)
    search_score_fk = models.ForeignKey(Searchspectrum_Query)

    def __unicode__(self):
        return self.ionscore

# The models from the mzML section


class Experiment(models.Model):
    fileuser = models.CharField(max_length=25)
    filename = models.CharField(max_length=40)
    uploaddate = models.CharField(max_length=15)
    size = models.CharField(max_length=20)
    located = models.CharField(max_length=100)

    def __unicode__(self):
        return self.user, self.filename


class mzML(models.Model):
    mzml_id = models.CharField(max_length=50, blank=True)
    accession = models.CharField(max_length=50, blank=True)
    version = models.CharField(max_length=50, blank=False)
    exp = models.ForeignKey(Experiment)  # many to one relationship

    def __unicode__(self):
        return self.mzml_id, self.accession


class Source_File(models.Model):
    sf_id = models.CharField(max_length=50, blank=False)
    name = models.CharField(max_length=60, blank=False)
    location = models.CharField(max_length=70, blank=False)
    mzml_fk = models.ForeignKey(mzML)  # many to one relationship

    def __unicode__(self):
        return self.name


class Source_file_CV(models.Model):
    accession = models.CharField(max_length=50, blank=False)
    name = models.CharField(max_length=50, blank=False)
    value = models.CharField(max_length=100)
    sf_fk = models.ForeignKey(Source_File)  # many to one relationship

    def __unicode__(self):
        return self.name


class Software(models.Model):
    soft_id = models.CharField(max_length=45)
    version = models.CharField(max_length=50, blank=False)
    soft_fk = models.ForeignKey(mzML)

    def __unicode__(self):
        return self.soft_id


class Software_CV(models.Model):
    accession = models.CharField(max_length=45, blank=False)
    name = models.CharField(max_length=45, blank=False)
    value = models.CharField(max_length=45, blank=True)
    soft_cv_fk = models.ForeignKey(Software)

    def __unicode__(self):
        return self.name


class DataProcessing(models.Model):
    dp_id = models.CharField(max_length=50)
    data_fk = models.ForeignKey(mzML)

    def __unicode__(self):
        return self.dp_id


class Data_Pro_Method(models.Model):
    p_soft_ref = models.CharField(max_length=60, blank=False)
    data_p_fk = models.ForeignKey(DataProcessing)

    def __unicode__(self):
        return self.p_soft_ref


class Data_Pro_CV(models.Model):
    accession = models.CharField(max_length=45, blank=False)
    name = models.CharField(max_length=50, blank=False)
    value = models.CharField(max_length=45, blank=True)
    pro_meth_fk = models.ForeignKey(Data_Pro_Method)

    def __unicode__(self):
        return self.name


class InstrumentConfiguration(models.Model):
    ins_id = models.CharField(max_length=15)
    ins_pro_fk = models.ForeignKey(mzML)

    def __unicode__(self):
        return self.ins_id


class InsConSource(models.Model):
    accession = models.CharField(max_length=45, blank=False)
    name = models.CharField(max_length=60, blank=False)
    value = models.CharField(max_length=45, blank=True)
    inss_fk_id = models.ForeignKey(InstrumentConfiguration)

    def __unicode__(self):
        return self.name


class InsConAnalyzer(models.Model):
    accession = models.CharField(max_length=45, blank=False)
    name = models.CharField(max_length=60, blank=False)
    value = models.CharField(max_length=45, blank=True)
    insa_fk_id = models.ForeignKey(InstrumentConfiguration)

    def __unicode__(self):
        return self.name


class InsConDetector(models.Model):
    accession = models.CharField(max_length=45, blank=False)
    name = models.CharField(max_length=60, blank=False)
    value = models.CharField(max_length=45, blank=True)
    insd_fk_id = models.ForeignKey(InstrumentConfiguration)

    def __unicode__(self):
        return self.name


class SelectedIon(models.Model):
    monoiso = models.FloatField()
    chargestate = models.CharField(max_length=2)
    peakinten = models.CharField(max_length=20)
    sele_fk = models.ForeignKey(mzML, related_name="mzmlid_set")

    def __unicode__(self):
        return str(self.monoiso)


class Spectrum(models.Model):
    spec_id = models.CharField(max_length=60, blank=False)
    spec_index = models.IntegerField(blank=False)
    spec_defaultarraylength = models.IntegerField(blank=False)
    identified = models.CharField(max_length=2)
    spec_fk = models.ForeignKey(SelectedIon)

    def __unicode__(self):
        return str(self.spec_id)


class Spectrum_CV(models.Model):
    accession = models.CharField(max_length=45, blank=False)
    name = models.CharField(max_length=60, blank=False)
    value = models.CharField(max_length=45, blank=True)
    spec_cv_fk = models.ForeignKey(Spectrum)

    def __unicode__(self):
        return self.name


class Scan(models.Model):
    accession = models.CharField(max_length=45, blank=False)
    name = models.CharField(max_length=80, blank=False)
    value = models.CharField(max_length=200, blank=True)
    scan_fk = models.ForeignKey(Spectrum)

    def __unicode__(self):
        return self.name

class ScanWindow(models.Model):
    accession = models.CharField(max_length= 45, blank=False)
    name = models.CharField(max_length=80, blank=False)
    value = models.CharField(max_length=200, blank=True)
    scanw_fk= models.ForeignKey(Spectrum)

    def __unicode__(self):
        return self.name