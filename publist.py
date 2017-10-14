# -*- coding: utf-8 -*-
import urllib
import codecs
import tempfile
import sys

class ADSEntry(object):
    def __init__(self, ads_id):
        ads_id = ads_id.replace('&', '%26') # remove '&' for URL
        url = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?bibcode=%s&data_type=ENDNOTE&return_fmt=LONG' % ads_id
        sys.stderr.write('Downloading %s\n' % url)
        temp = tempfile.TemporaryFile()
        urllib.urlretrieve(url, temp.name)
        f = codecs.open(temp.name, 'r', 'iso-8859-1')
        self.endnote = f.read()
        f.close()

        self.getAuthorNames()
        self.getJournal()

    def getAuthorNames(self):
        self.authors = []

        # Retrieve author names
        for line in self.endnote.split('\n'):
            if line.find('%A ') == 0: # EndNote tag for an author
                line = line.split('%A ')[1]
                while line[-1] == u' ':
                    line = line[:-1]
                line = line.replace(u' ', u'\u00a0') # Replace white spaces with non-braking spaces

                # Drop collaboration name
                if line.find('collaboration') >= 0 or\
                   line.find('Collaboration') >= 0 or\
                   line.find('consortium') >= 0 or\
                   line.find('Consortium') >= 0 or\
                   line.find('team') >= 0 or\
                   line.find('Team') >= 0:
                    pass
                else:
                    self.authors.append(line)

    def getJournal(self):
        # Retrieve journal information
        for line in self.endnote.split('\n'):
            if line.find('%T ') == 0: # EndNote tag for title
                self.title = line.split('%T ')[1]
            elif line.find('%D ') == 0: # EndNote tag for year
                self.year = line.split('%D ')[1]
            elif line.find('%P') == 0: # EndNote tag for pages
                self.pages = line.split('%P ')[1].replace('-', u'–')
            elif line.find('%V ') == 0: # EndNote tag for volume
                self.volume = line.split('%V ')[1]
            elif line.find('%B ') == 0: # EndNote tag for journal
                line = line.split('%B ')[1]
                abbr_dict = {'Monthly Notices of the Royal Astronomical Society': 'Mon. Not. R. Astron. Soc.',
                             'The Astrophysical Journal': 'Astrophys. Jour.',
                             'The Astrophysical Journal Letters': 'Astrophys. Jour. Lett.',
                             'Astrophys. Jour. Letters': 'Astrophys. Jour. Lett.',
                             'The Astrophysical Journal Supplement Series': 'Astrophys. Jour. Suppl. Ser.',
                             'Astroparticle Physics': 'Astropart. Phys.',
                             'Physical Review Letters': 'Phys. Rev. Lett.',
                             'Science': 'Science',
                             'Nature': 'Nature',
                             'Astronomy and Astrophysics': 'Astron. Astrophys.',
                             'Journal of Instrumentation': 'JINST',
                             'Nuclear Instruments and Methods in Physics Research A': 'Nucl. Instr. Meth. Phys. Res.A'}

                try:
                    line = abbr_dict[line]
                except:
                    pass

                self.journal = line

    def formatAuthors(self, ul_authors, cor_authors = (), maximum = 5, firstlast = True):
        s = u''

        if firstlast:
            for i, author in enumerate(self.authors):
                try:
                    last, first = author.split(u',\u00a0')
                except:
                    raise BaseException(author.split(u',\u00a0')[0])
                self.authors[i] = u'%s\u00a0%s' % (first, last)

        total = len(self.authors)

        if total <= maximum:
            for author in self.authors:
                if author == self.authors[-1] and total != 1:
                    s += 'and '

                if author.replace(u'\u00a0', u' ') in cor_authors:
                    author = '*' + author

                if author.replace(u'\u00a0', u' ').replace('*', '') in ul_authors:
                    s += u'<u>%s</u>, ' % author
                else:
                    s += u'%s, ' % author
            return s[:-2]
        else:
            for i, author in enumerate(self.authors):
                if i == 0:
                    if author.replace(u'\u00a0', u' ') in cor_authors:
                        author = '*' + author

                    if author.replace(u'\u00a0', u' ').replace('*', '') in ul_authors:
                        s += u'<u>%s</u>, ' % author
                    else:
                        s += u'%s, ' % author

                    total -= 1
                elif author.replace(u'\u00a0', u' ') in ul_authors or author.replace(u'\u00a0', u' ') in cor_authors:
                    if author.replace(u'\u00a0', u' ') in cor_authors:
                        author = '*' + author

                    n = i + 1
                    order = u'%d' % n
                    if n%100 in (11, 12, 13):
                        order += u'th'
                    elif n%10 == 1:
                        order += u'st'
                    elif n%10 == 2:
                        order += u'nd'
                    elif n%10 == 3:
                        order += u'rd'
                    else:
                        order += u'th'

                    if author.replace(u'\u00a0', u' ').replace('*', '') in ul_authors:
                        s += u'<u>%s</u> (%s), ' % (author, order)
                    else:
                        s += u'%s (%s), ' % (author, order)
                    total -= 1

            s += u'and %d coauthors' % total
            return s

    def getNewScientificFormat(self, ul_authors, cor_authors, maximum): # 新学術
        return u'“%s”, %s, <i>%s</i> <b>%s</b>, %s (%s)' % (self.title, self.formatAuthors(ul_authors, cor_authors, maximum, True), self.journal, self.volume, self.pages, self.year)

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

    print u'<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head><body style="font-size : 10pt">'
    print u'<ol>'

    okumura = (u'A. Okumura', u'Akira Okumura')
    tajima = (u'H. Tajima', u'Hiroyasu Tajima')
    ul_authors = okumura + tajima
    for ads in (('2017APh....92...49A', okumura), ('2016APh....76...38O', okumura)):
        print u'<li>',
        print ADSEntry(ads[0]).getNewScientificFormat(ul_authors, ads[1], 10),
        print u'</li>'

    print u'</ol>'
    print u'</body>'
