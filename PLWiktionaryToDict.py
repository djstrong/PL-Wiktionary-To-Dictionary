#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Copyright (c) 2012, Krzysztof Wróbel <djstrong / gmail>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the FreeBSD Project.
'''

import sys
import re
import locale

class Entry:
    """Represents one translation of some entry.
    
    Attributes:
        word: A string representing entry.
        language: A string representing language of entry.
        meanings: A list of strings representing meaning of entry in Polish.
    """
    
    def __init__(self, entry):
        """Template method.
        
        Args:
            entry: A string of raw entry.
        """
        self.__parse_word_and_language(entry)
        self.__parse_meanings(entry)
        self.__parse_forms(entry)
        
        self.__normalize_meanings()
        
    def __normalize_meanings(self):
        """Clears wiki formatting to plain text.
        
        Raises:
            ValueError: An error occured when meanings and forms are empty.
        """
        t = self.meanings
        if self.forms is not None:
            t += self.forms
            
        if not t:
            raise ValueError("no meanings - __normalize_meanings")
            
        #TODO: POS
        m = re.findall(': ?\([0-9.]+\) ?(.*)', t)
        self.meanings = []
        for meaning in m:
            meaning = re.sub("\[\[(.*?)\]\]", '\\1', meaning) 
            
            #bold
            meaning = re.sub("'''(.*?)'''", '\\1', meaning) 
            
            meaning = re.sub('{{.*?}}', '', meaning)
            
            #links
            meaning = re.sub("''\(.*?''", '', meaning)
            meaning = re.sub("\(''.*?''\)", '', meaning)
            meaning = re.sub("''.*?''", '', meaning)
            
            #refs
            meaning = re.sub("&lt;ref( name=(&quot;)?.*?(&quot;)?)?&gt;.*?&lt;/ref&gt;", '', meaning)
            meaning = re.sub("&lt;ref( name=(&quot;)?.*?(&quot;)?)?/&gt;", '', meaning)

            #odmiany
            meaning = re.sub('[^( ]+\|([^) ]+)', '\\1', meaning)
            
            #arrow
            meaning = re.sub('.*?→', '', meaning)
            
            #puste nawiasy
            meaning = re.sub('\( *\)', '', meaning)

            #spacje z przecinkami
            meaning = re.sub(' *, *', ', ', meaning)
            meaning = re.sub('\( +', '(', meaning)
            meaning = re.sub(' +\)', ')', meaning)

            meaning = meaning.strip(' ,')

            if meaning:
                self.meanings.append(meaning)
        
        if not self.meanings:
            raise ValueError('no meanings - __normalize_meanings2')

    def __parse_forms(self, entry): #TODO: sang is not parsed - forma czasownika/rzeczownika
        """Parses forms of entry.
        
        Args:
            entry: A string of raw entry.
        """
        m = re.search('\n{{forma .*?}}(.*?)\n{{', entry, re.S)
        if m is not None:
            self.forms = m.group(1).strip()
        else:
            self.forms = None
        
    def __parse_meanings(self, entry):
        """Parses meanings of entry.
        
        Args:
            entry: A string of raw entry.
        
        Raises:
            ValueError: An error occured when no meanings tag.
        """
        m = re.search('{{znaczenia}}(.*?)\n{{', entry, re.S)
        if m is not None:
            self.meanings = m.group(1).strip()
        else:
            print >> sys.stderr, '__parseMeanings(): probably lack of meanings: ' + entry
            raise ValueError("no meanings tag")
        
    def __parse_word_and_language(self, entry):
        """Parses word and language of entry.
        
        Args:
            entry: A string of raw entry.
            
        Raises:
            ValueError: An error occured when no word or language..
        """
        m = re.search('== (.*?) \({{(.*?)(?:\|.*?)?}}\) ==', entry)
        if m is not None:
            self.word = m.group(1).strip()
            self.word = re.sub("\[\[(.*?)\]\]", '\\1', self.word) 
            self.word = re.sub('[^( ]+\|([^) ]+)', '\\1', self.word)
            
            self.language = m.group(2).strip()
            #print self.language
        else:
            print >> sys.stderr, '__parseWordAndLanguage(): probably lack of space between entry and language: ' + entry
            raise ValueError('__parseWordAndLanguage')

class Page:
    """Represents page of wiktionary.
    
    Attributes:
        title: A string with title of page.
        entries: A list of Entry objects 
    """
    
    def __init__(self, content):
        """Parses page of wiktionary.
        
        Args:
            content: A string with page.
        
        Raises:
            ValueError: An error occured parsing page.
        """
        self.title = title = self.__parse_title(content)
        
        if re.search('^[ 0-9]+$', title) is not None or title.startswith(('Słownik ', 'Wikipedysta:', 'Dyskusja wikipedysty:', 'Szablon:', 'Dyskusja:', 'Indeks:', 'Kategoria:', 'Pomoc:', 'MediaWiki:', 'Aneks:', 'Dyskusja MediaWiki:', 'Dyskusja aneksu:', 'Dyskusja indeksu:', 'Dyskusja szablonu:', 'Dyskusja kategorii:', 'Wikisłownik:', 'Wikidyskusja:', 'Portal:', 'Plik:', 'Dyskusja portalu:', 'Dyskusja użytkownika', 'Dyskusja pomocy')):
            raise ValueError("not an entry")
        
        m = re.search('<text xml:space="preserve">(.*?)</text>', content, re.S) 
        if m is None:
            print >> sys.stderr, 'parsePage(): no text in page with title: ' + title
            raise ValueError("no entries: no text tag")
        text = m.group(1)
        
        if text.startswith(('#REDIRECT', '#redirect', '#PATRZ', '#patrz', '#TAM', '#tam')): #TODO: what with it?
            raise ValueError("no entries: redirect")
        elif text.startswith('#'):
            print >> sys.stderr, 'parsePage(): undefined hash started text: ' + title
            raise ValueError("no entries: hash started")
                
        entries = self.__parse_entries(text)
        
        if entries is None:
            print >> sys.stderr, 'parsePage(): probably bad format: ' + title
            raise ValueError("no entries")
        
        self.entries = []
        for entry in entries:
            try:
                e = Entry(entry)
            except ValueError as err:
                continue
            self.entries.append(e)
    
    def __parse_title(self, text):
        """Parses title of page.
        
        Args:
            text: A string with page.
        
        Returns:
            A string with title of page.
        """
        m = re.search('<title>(.*?)</title>', text)
        if m is None:
            return None
        return m.group(1)
    
    def __fix_new_lines(self, text):
        """Fixes new lines between entries in page.
        
        Args:
            text: A string with raw entries.
            
        Returns:
            A string with fixed new lines.
        """
        text = re.sub('\n{2,}', '\n', text)
        text = re.sub('(== .*? ==)', '\n\\1', text)
        text = re.sub('\n{3,}', '\n\n', text)
        text = text.replace("\n\n", "\n", 1)
        return text
    
    def __parse_entries(self, text):
        """Parses entries in page.
        
        Args:
            text: A string with raw entries.
            
        Returns:
            A list of strings with entries.
        """
        m2 = re.findall('== .*? ==.*?(?:\n\n|$)', text, re.S)
        m3 = re.findall('== .*? ==', text)
        
        if len(m2) != len(m3):
            print >> sys.stderr, 'parseEntries(): probably bad format with new lines: ' + self.title
        
        text = self.__fix_new_lines(text)
        m2 = re.findall('== .*? ==.*?(?:\n\n|$)', text, re.S)
        m3 = re.findall('== .*? ==', text)
        
        if m2 is None or not m2:
            print >> sys.stderr, 'parseEntries(): probably bad format with meanings format: ' + self.title
            return None
        
        return m2

class PLWiktionaryToDictionary:
    """Parser of polish wiktionary dump and checker of some wiktionary formats (stderr). Implements iterator.
    
    Attributes:
        dictionary: A list of entries.
    """
    
    _WIKI_LANGUAGES = set("nagłówek języka,termin obcy w języku polskim,termin obcy w języku łacińskim,dżuhuri,esperanto,ewe,hindi,ido,interlingua,inuktitut,język kaszmirski,język marathi,język newarski,język sorani,język zazaki,ladino,lingala,novial,papiamento,pitjantjatjara,sanskryt,slovio,sranan tongo,tetum,tok pisin,tupinambá,użycie międzynarodowe,volapük,znak chiński,brithenig,esperanto (morfem),jidysz,jèrriais,język !Xóõ,język a-pucikwar,język abazyński,język abchaski,język abenaki,język adygejski,język afar,język afrykanerski,język ajmara,język akadyjski,język aklanon,język alabama,język albański,język alemański,język aleucki,język ama,język amharski,język angielski,język arabski,język aragoński,język aramejski,język arapaho,język arczyński,język arumuński,język assamski,język asturyjski,język awarski,język azerski,język bambara,język banjumasański,język baskijski,język baszkirski,język bawarski,język beludżi,język bengalski,język białoruski,język białoruski (taraszkiewica),język birmański,język bislama,język boloński,język bośniacki,język bretoński,język bugijski,język bułgarski,język cebuano,język chakaski,język chantyjski (kazymski),język chantyjski (surgucki),język chantyjski (szuryszkarski),język chantyjski (wachowski),język chickasaw,język chiński standardowy,język chorwacki,język czagatajski,język czamorro,język czarnogórski,język czeczeński,język czeski,język czirokeski,język czuwaski,język dalmatyński,język dari,język dolnoniemiecki,język dolnołużycki,język duński,język dzongkha,język erzja,język estoński,język etruski,język farerski,język fenicki,język fidżyjski,język filipino,język fiński,język francuski,język friulski,język fryzyjski,język fryzyjski saterlandzki,język ful,język ga,język gagauski,język galicyjski,język gaskoński,język gocki,język grenlandzki,język gruziński,język guarani,język gudźarati,język gyyz,język górnołużycki,język haitański,język hausa,język hawajski,język hebrajski,język hiligaynon,język hiszpański,język holenderski,język hupa,język ilokano,język indonezyjski,język inguski,język irlandzki,język islandzki,język istriocki,język jakucki,język japoński,język jawajski,język jaćwieski,język joruba,język kabylski,język kakczikel,język kannada,język karaczajsko-bałkarski,język karakałpacki,język karelski,język kaszubski,język kataloński,język kazachski,język kałmucki,język keczua,język khmerski,język kirgiski,język klingoński,język komi,język komi-jaźwiński,język komi-permiacki,język komi-zyriański,język konkani,język koptyjski,język koreański,język kornijski,język korsykański,język kri,język krymskotatarski,język kumycki,język kurdyjski,język kurmandżi,język ladyński,język langwedocki,język laotański,język lazyjski,język lezgiński,język liguryjski,język limburski,język litewski,język lombardzki,język luksemburski,język luo,język macedoński,język malajalam,język malajski,język malediwski,język malgaski,język maltański,język manx,język maoryski,język maryjski,język mazanderański,język mikmak,język minnan,język moksza,język mongolski,język motu,język mołdawski,język nahuatl,język nauruański,język nawaho,język neapolitański,język neo,język nepalski,język niemiecki,język normandzki,język norweski (bokmål),język norweski (nynorsk),język nowogrecki,język orija,język ormiański,język oromo,język osetyjski,język osmańsko-turecki,język pali,język paszto,język pendżabski,język pensylwański,język perski,język piemoncki,język pikardyjski,język pirahã,język plautdietsch,język polski,język portugalski,język połabski,język pragermański,język prowansalski,język pruski,język północnofryzyjski,język północnolapoński,język rarotonga,język romansz,język romski,język rosyjski,język rumuński,język rundi,język rusiński,język russenorsk,język sardyński,język serbski,język serbsko-chorwacki,język shelta,język shona,język sindhi,język sko,język skolt,język somalijski,język staro-cerkiewno-słowiański,język staro-wysoko-niemiecki,język staroangielski,język staroegipski,język starofrancuski,język starogrecki,język staroirlandzki,język staronordyjski,język staroormiański,język staroruski,język suahili,język sumeryjski,język sundajski,język susu,język sycylijski,język syngaleski,język szerpa,język szkocki,język szkocki gaelicki,język szorski,język szwabski,język szwedzki,język słowacki,język słoweński,język słowiński,język tabasarański,język tadżycki,język tagalski,język tahitański,język tajski,język tamaszek,język tamazight,język tamilski,język tashelhiyt,język tatarski,język telugu,język tigrinia,język tonga,język turecki,język turkmeński,język tuvalu,język tuwiński,język twi,język tybetański,język udmurcki,język ujgurski,język ukraiński,język urdu,język uwea,język uzbecki,język võro,język walijski,język waloński,język warajski,język wczesny nowoangielski,język wenecki,język wepski,język wietnamski,język wilamowski,język wolof,język wysokoislandzki,język węgierski,język włoski,język xhosa,język yupik środkowy,język zachodnioflamandzki,język zarfatit,język zelandzki,język zulu,język łaciński,język łatgalski,język łotewski,język średnio-dolno-niemiecki,język średnio-wysoko-niemiecki,język średnioangielski,język żmudzki,Lingua Franca Nova,quenya,romániço,wenedyk".split(','))
    
    def __init__(self, path, language='język angielski'):
        """Opens wiktionary dump and sets language of dictionary.
        
        Args:
            path: A string representing path to wiktionary dump.
            language: A string in polish representing language of dictionary.
        """
        self.f = open(path, 'r')
        self.dictionary = []
        self.language = language
        if language not in self._WIKI_LANGUAGES:
            print >> sys.stderr, 'unknown language in argument: ' + language
    
    def __iter__(self):
        return self.__entries()
    
    def __entries(self):
        """A generator yielding entries in language."""
        generator = self.__parse()
        for page in generator:
            for e in page.entries:
                if e.language not in self._WIKI_LANGUAGES:
                    print >> sys.stderr, 'unknown language: ' + e.language + ' word: ' + e.word

                if e.language == self.language:
                    self.dictionary.append(e)
                    yield(e)
        
    def __parse(self):
        """A generator yielding pages of wiktionary."""
        for line in self.f:
            
            if line.strip() == '<page>':
                content = line
                for line in self.f:
                    content += line
                    
                    if line.strip() == '</page>':
                        break
                    
                try:
                    page = Page(content)
                except ValueError:
                    continue

                yield page

    def __del__(self):
        self.f.close()

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL,"")
    
    path = sys.argv[1]
    if len(sys.argv)==3:
        lang = sys.argv[2]
        w = PLWiktionaryToDictionary(path, language=lang)
    else:
        w = PLWiktionaryToDictionary(path)
    #w = PLWiktionaryToDictionary('plwiktionary-20120718-pages-meta-current.xml2')
    for e in sorted(w, key=lambda x: x.word, cmp=locale.strcoll):
        print '%s - %s' % (e.word, '; '.join(e.meanings))