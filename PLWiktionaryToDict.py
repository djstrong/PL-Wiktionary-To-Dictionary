#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (c) 2012, Krzysztof Wróbel <djstrong.dev@gmail.com>
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
import collections


class EntryDefault:
    """Represents one translation of some entry.
    
    Attributes:
        word: A string representing entry.
        language: A string representing language of entry.
        meanings: A list of strings representing meaning of entry in Polish.
        translations: Refers to Polish entries. A list of string tuples representing language and translation of entry in that language.
    """
    
    def __init__(self, entry):
        """Template method.
        
        Args:
            entry: A string of raw entry.
        """
        
        #print entry,'\n\n\n'
        
        self._parse_word_and_language(entry)
        
        if self.language == 'język polski':
            self._parse_translations(entry)
            self._normalize_translations()
        else:
            self._parse_meanings(entry)
            #print 'M', self.meanings, self.word
            self._parse_forms(entry)
           # if self.forms: print 'F', self.forms, self.word
            self._normalize_meanings()

    def rozdziel(self, text):
        slowa = []
        w = w2 = w3 = w4 = False
        last = 0
        for i in xrange(len(text)):
            #print text[i]
            if not w and not w2 and not w3 and not w4 and text[i:i+2] in (', ', '; '):
                #print 'apend'
                slowa.append(text[last:i])
                last=i+2
            else:
                #print text[i:i+2], text[i:i+2]=='[[', text[i:i+2]==']]', w
                if text[i:i+2]=='[[':
                    w = True
                elif text[i:i+2]==']]':
                    w = False
                elif text[i:i+2]=='{{':
                    w2 = True
                elif text[i:i+2]=='}}':
                    w2 = False
                elif text[i]=='(':
                    w3 = True
                elif text[i]==')':
                    w3 = False
                elif text[i:i+2]=="''":
                    w4 = not w4

        if last+1<len(text):
            slowa.append(text[last:])
        return slowa

    def _normalize_meanings(self):
        """Clears wiki formatting to plain text.
        
        Raises:
            ValueError: An error occured when meanings and forms are empty.
        """
        t = self.meanings
        if self.forms is not None:
            t += self.forms
            
        if not t:
            raise ValueError("no meanings - _normalize_meanings")
            
        # TODO: POS
        m = re.findall('.*\n: ?\([0-9.]+\) ?(.*)', t)
        # print m,t
        self.meanings = []
        for meaning in m:
            
            meaning = re.sub('<ref( name=(")?.*?(")?)?>.*?</ref>', '', meaning)
            meaning = re.sub('<ref( name=(")?.*?(")?)?/>', '', meaning)

            meaning=meaning.strip()
            slowa = self.rozdziel(meaning)
            
            for slowo in slowa:
                
                slowo = re.sub("\[\[(.*?)\]\]", lambda x: x.group(1)[x.group(1).index('|')+1:] if '|' in x.group(1) else x.group(1), slowo)
                slowo = re.sub("''(.*?)''", '', slowo)
                
                slowo = re.sub('{{(.{2,}?)}}', lambda x: '' if len(x.group(1).split('|'))==1 else x.group(1).split('|')[1], slowo)
                slowo = re.sub('{{(.{2,}?)}}', '', slowo)
                slowo = re.sub('{{([mnfw])}}', '\\1', slowo)
                slowo = re.sub('{{.}}', '', slowo)
                
                # puste nawiasy
                slowo = re.sub('\( *\)', '', slowo)
                
                index = slowo.rfind('→')
                if index!=-1:
                    slowo=slowo[index+1:]
                    #print 'SLOWO:', slowo, 'WORD:', self.word, 'SLOWA:', ' | '.join(slowa)
                
                slowo = re.sub(' {2,}', ' ', slowo)
                
                slowo=slowo.strip()
                if '→' in slowo:
                    print >> sys.stderr, 'SLOWO:', slowo, 'WORD:', self.word, 'SLOWA:', ' | '.join(slowa)
                #print 'S', slowo, meaning
                
                if slowo:
                    #print slowo
                    self.meanings.append(slowo)
                
#             print meaning
#             meaning = re.sub("\[\[(.*?)\]\]", '\\1', meaning) 
#             
#             # bold
#             meaning = re.sub("'''(.*?)'''", '\\1', meaning) 
#             
#             meaning = re.sub('{{.*?}}', '', meaning)
#             
#             # links
#             meaning = re.sub("''\(.*?''", '', meaning)
#             meaning = re.sub("\(''.*?''\)", '', meaning)
#             meaning = re.sub("''.*?''", '', meaning)
#             
#             # refs
#             meaning = re.sub("&lt;ref( name=(&quot;)?.*?(&quot;)?)?&gt;.*?&lt;/ref&gt;", '', meaning)
#             meaning = re.sub("&lt;ref( name=(&quot;)?.*?(&quot;)?)?/&gt;", '', meaning)
# 
#             # odmiany
#             meaning = re.sub('[^( ]+\|([^) ]+)', '\\1', meaning)
#             
#             # arrow
#             meaning = re.sub('.*?→', '', meaning)
#             
#             # puste nawiasy
#             meaning = re.sub('\( *\)', '', meaning)
# 
#             # spacje z przecinkami
#             meaning = re.sub(' *, *', ', ', meaning)
#             meaning = re.sub('\( +', '(', meaning)
#             meaning = re.sub(' +\)', ')', meaning)
# 
#             meaning = meaning.strip(' ,')
# 
#             if meaning:
#                 self.meanings.append(meaning)
        
        if not self.meanings:
            raise ValueError('no meanings - __normalize_meanings2')

    def _parse_forms(self, entry):  # TODO: sang is not parsed - forma czasownika/rzeczownika
        """Parses forms of entry.
        
        Args:
            entry: A string of raw entry.
        """
        m = re.search('\n{{forma .*?}}(.*?)\n{{', entry, re.S)
        if m is not None:
            self.forms = m.group(1).strip()
        else:
            self.forms = None
        
    def _parse_meanings(self, entry):
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
        
    def _parse_word_and_language(self, entry):
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
            # print entry, self.word TODO rodzaj
            self.language = m.group(2).strip()
            # print self.language
            
            m2 = re.search("''rzeczownik, rodzaj (.*?)''", entry)
            if m2 is not None:
                # print m2.group(1), self.language, self.word
                self.gender = m2.group(1)
            
            
        else:
            print >> sys.stderr, '__parseWordAndLanguage(): probably lack of space between entry and language: ' + entry
            raise ValueError('__parseWordAndLanguage')

class EntryPolish (EntryDefault):
    def __init__(self, entry):
        self._parse_word_and_language(entry)


        m = re.search('== (.*?) \({{(.*?)(?:\|.*?)?}}\) ==', entry)
        
        
        self._parse_translations(entry)
        
        #print self.word, m.group(0), self.translations
        self._normalize_translations()
        

        
    def _normalize_translations(self):
        """Clears wiki formatting in translations to plain text.
        
        Raises:
            ValueError: An error occured when translations are empty.
        """
        t = self.translations
            
        if not t:
            raise ValueError("_normalize_translations: no translations")
            
        # TODO: {{zobtłum|}}
        # TODO: POS
        
        m1 = re.findall(u'{{zobtłum\|(.*?)}}', t)
        if m1:
            self.zobtlum = []
            for x in m1:
                self.zobtlum.extend(x.split('|'))
            #print map(lambda x: x.split('|'), m1)
            #print m1, self.word
            #print self.zobtlum
        m = re.findall('\* ([^:]+): (.*)', t)
        
        #if u'zobtłum' in t:
        #    print 'XXXX',t
            #print m
        if not m and 'zobtłum' not in t:
            print >> sys.stderr, '_normalize_translations(): probably lack of space in translations: ' + self.word
            
        self.translations = []
        for lang, translation in m:
            #TODO poprawic dzielenie znaczen
            # [[word]] -> word
            #print 'T', translation, lang, self.word
            if (lang==u'polski język migowy'): continue
            
            #m2 = re.findall('\([0-9]+(?:\.[0-9]+)*(?:[,-] ?[0-9]+(?:\.[0-9]+)*)*\).+?(?:\([0-9]+(?:\.[0-9]+)*(?:[,-] ?[0-9]+(?:\.[0-9]+)*)*\))?', translation)
            #m2=re.findall('[0-9]+\.(?:(?![0-9]+\.).)*', translation)
            #print m2
            translations = []
            for meaning in translation.split(';'):
                meaning=meaning.strip()
                #numery i transliteracje
                meaning = re.sub('\([0-9]+.*?\)', '', meaning)
                
                #m2 = re.search('{{(.)}}', meaning)
                #if m2: 
                #    print m2.group(0)
                #    print 'M', meaning, self.word
                
                #zostawiamy rodzajniki
                #meaning = re.sub('{{(.)}}', '\\1', meaning)
                #wyrzucamy skroty
                #meaning = re.sub('{{(.*?)}}', '', meaning)
                
                # refs
                meaning = re.sub('<ref( name=(")?.*?(")?)?>.*?</ref>', '', meaning)
                meaning = re.sub('<ref( name=(")?.*?(")?)?/>', '', meaning)

                meaning=meaning.strip()

                #ll = [u'angielski', u'niemiecki', u'francuski', u'hiszpański', u'włoski', u'rosyjski', u'czeski', u'słowacki', u'ukraiński', u'holenderski',
                # u'turecki', u'duński', u'bułgarski', u'portugalski', u'chorwacki', u'fiński', u'norweski', u'litewski', u'łotewski', u'estoński'
                # , u'szwedzki', u'łaciński', u'nowogrecki', u'arabski', u'esperanto', u'interlingua', u'jidysz', u'gruziński', u'węgierski', u'kataloński', u'japoński', u'koreański']
                
                #if lang!='asd':
                slowa = self.rozdziel(meaning)
                
                for slowo in slowa:
                    slowo = re.sub("\[\[(.*?)\]\]", lambda x: x.group(1)[x.group(1).index('|')+1:] if '|' in x.group(1) else x.group(1), slowo)
                    slowo = re.sub("''(.*?)''", '', slowo)
                    
                    slowo = re.sub('{{(.{2,}?)}}', lambda x: '' if len(x.group(1).split('|'))==1 else x.group(1).split('|')[1], slowo)
                    slowo = re.sub('{{(.{2,}?)}}', '', slowo)
                    slowo = re.sub('{{([mnfw])}}', '\\1', slowo)
                    slowo = re.sub('{{.}}', '', slowo)
                    
                    # puste nawiasy
                    slowo = re.sub('\( *\)', '', slowo)
                    

                    #zle dzielone arabskie ,
                    if '→' in slowo:
                        print >> sys.stderr, 'SLOWO:', slowo, 'WORD:', self.word, 'SLOWA:', ' | '.join(slowa)
                
                    slowo = re.sub(' {2,}', ' ', slowo)
                    slowo=slowo.strip()
                
                    if slowo and slowo not in translations:
                        translations.append(slowo)
                        #niedodawac jesli juz jest
             
            self.translations.append((lang, translations))
            #if not translations: print ' | '.join(translations), 'XXX', translation, self.word
                    #continue
                    #meaning = re.sub('\(.*?\)', '', meaning)
                    
                    #wyrzucamy skroty
                    
                    
                    #wyrzucamy przypisy
                    #meaning = re.sub('{{(.{2,})}}', '', meaning)
                    
                    #meaning=meaning.strip()
                    
                    #print 'M', meaning, lang, self.word
                    
                    #m3 = re.search('^(\[\[[^\[\]]*?\]\]\'?\w*(?: +{{[mfwn]}})?)(?: *[,/!-]? *(\[\[[^\[\]]*?\]\]\'?\w*(?: +{{[mfwn]}})?))*$', meaning)
                    #m3 = None
                    
                    #if not m3 : 
                    #    print 'M', meaning, lang, self.word
                    #else:
                    #    print m3.group(0), meaning
                #
                #if meaning and meaning[0]!='[':
                    

                #m2 = re.search('\([0-9]+(\.[0-9]+)*(?:[,-] ?[0-9]+(\.[0-9]+)*)*\)', meaning)
                #if not m2:
                #    print 'M', meaning, 'T', translation, lang, self.word
                    #print m2.group(0)
            
            #translation = re.sub("\[\[(.*?)\]\]", '\\1', translation) 
            
            # bold
            # meaning = re.sub("'''(.*?)'''", '\\1', meaning) 
            
            # rodzaj gramatyczny
            #if lang == 'niemiecki' or lang == 'francuski':
            #    translation = re.sub('{{(.*?)}}', '\\1', translation)
            #else:
            #    translation = re.sub('{{(.*?)}}', '', translation)
                
            # transliteracje i numery
            
            
            # podwojne spacje
            #translation = re.sub(' {2,}', ' ', translation)
            
            # links
            # meaning = re.sub("''\(.*?''", '', meaning)
            # meaning = re.sub("\(''.*?''\)", '', meaning)
            # meaning = re.sub("''.*?''", '', meaning)
            
            # refs
            #translation = re.sub("&lt;ref( name=(&quot;)?.*?(&quot;)?)?&gt;.*?&lt;/ref&gt;", '', translation)
            #translation = re.sub("&lt;ref( name=(&quot;)?.*?(&quot;)?)?/&gt;", '', translation)

            # odmiany
            # meaning = re.sub('[^( ]+\|([^) ]+)', '\\1', meaning)
            
            # arrow
            # meaning = re.sub('.*?→', '', meaning)
            
            # puste nawiasy
            # meaning = re.sub('\( *\)', '', meaning)

            # spacje z przecinkami
            # meaning = re.sub(' *, *', ', ', meaning)
            # meaning = re.sub('\( +', '(', meaning)
            # meaning = re.sub(' +\)', ')', meaning)

            #translation = translation.strip(' ,')

            #if translations:
            #    #print translation
            #    tts = []
            #    for tt in translation.split(';'):
            #        # print tt
            #        for tt2 in tt.split(','):
            #            tts.append(tt2.strip())
            #    
            #    self.translations.append((lang.strip(), ", ".join(unique(tts))))
                
        
        if not self.translations and not hasattr(self, 'zobtlum'):
            raise ValueError('no translations - _normalize_translations')
        
    def _parse_translations(self, entry):
        """Parses translations of Polish entry.
        
        Args:
            entry: A string of raw entry.
        
        Raises:
            ValueError: An error occured when no translation tag.
        """
        #print entry
        m = re.search(u'{{tłumaczenia}}(.*?)\n{{', entry, re.S)
        if m:
            self.translations = m.group(1).strip()
        else:
            print >> sys.stderr, '_parse_translations(): probably lack of translations: ' + entry
            raise ValueError("no translation tag")

class Fabric:
    mapa = {u'język polski':EntryPolish}
    
    @staticmethod
    def get_entry(entry):
        entry=entry.decode('utf-8')
        
        import HTMLParser
        h = HTMLParser.HTMLParser()
        entry = h.unescape(entry)
        
        language = Fabric.__parse_language(entry)
        #language=language.decode('utf-8')
        #print language, 'język polski', u'język polski'==language, language in Fabric.mapa, u'język polski' in Fabric.mapa
        
        if language in Fabric.mapa:
            return Fabric.mapa[language](entry)
        else:
            return EntryDefault(entry)
    
    @staticmethod
    def __parse_language(entry):
        """Parses language of entry.
        
        Args:
            entry: A string of raw entry.
            
        Raises:
            ValueError: An error occured when no word or language..
        """
        
        m = re.search('== (.*?) \({{(.*?)(?:\|.*?)?}}\) ==', entry)
        if m:
            language = m.group(2).strip()
            return language
        else:
            print >> sys.stderr, 'getEntry(): probably lack of space between entry and language: ' + entry
            raise ValueError('getEntry')

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
        
        if re.search('^[ 0-9]+$', title) is not None or title.startswith(('Słownik ', 'Wikipedysta:', 'Dyskusja wikipedysty:', 'Szablon:', 'Dyskusja:', 'Indeks:', 'Kategoria:', 'Pomoc:', 'MediaWiki:', 'Aneks:', 'Dyskusja MediaWiki:', 'Dyskusja aneksu:', 'Dyskusja indeksu:', 'Dyskusja szablonu:', 'Dyskusja kategorii:', 'Wikisłownik:', 'Wikidyskusja:', 'Portal:', 'Plik:', 'Dyskusja portalu:', 'Dyskusja użytkownika', 'Dyskusja pomocy','Module:')):
            raise ValueError("not an entry")
        
        m = re.search('<text xml:space="preserve">(.*?)</text>', content, re.S) 
        if m is None:
            print >> sys.stderr, 'parsePage(): no text in page with title: ' + title
            raise ValueError("no entries: no text tag")
        text = m.group(1)
        
        if text.startswith(('#REDIRECT', '#redirect', '#PATRZ', '#patrz', '#TAM', '#tam')):  # TODO: what with it?
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
                #e = Entry(entry)
                e = Fabric.get_entry(entry)
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
            # print >> sys.stderr, 'parseEntries(): probably bad format with new lines: ' + self.title
            pass
        
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
    
    _WIKI_LANGUAGES = set(u"nagłówek języka,termin obcy w języku polskim,termin obcy w języku łacińskim,dżuhuri,esperanto,ewe,hindi,ido,interlingua,inuktitut,język kaszmirski,język marathi,język newarski,język sorani,język zazaki,ladino,lingala,novial,papiamento,pitjantjatjara,sanskryt,slovio,sranan tongo,tetum,tok pisin,tupinambá,użycie międzynarodowe,volapük,znak chiński,brithenig,esperanto (morfem),jidysz,jèrriais,język !Xóõ,język a-pucikwar,język abazyński,język abchaski,język abenaki,język adygejski,język afar,język afrykanerski,język ajmara,język akadyjski,język aklanon,język alabama,język albański,język alemański,język aleucki,język ama,język amharski,język angielski,język arabski,język aragoński,język aramejski,język arapaho,język arczyński,język arumuński,język assamski,język asturyjski,język awarski,język azerski,język bambara,język banjumasański,język baskijski,język baszkirski,język bawarski,język beludżi,język bengalski,język białoruski,język białoruski (taraszkiewica),język birmański,język bislama,język boloński,język bośniacki,język bretoński,język bugijski,język bułgarski,język cebuano,język chakaski,język chantyjski (kazymski),język chantyjski (surgucki),język chantyjski (szuryszkarski),język chantyjski (wachowski),język chickasaw,język chiński standardowy,język chorwacki,język czagatajski,język czamorro,język czarnogórski,język czeczeński,język czeski,język czirokeski,język czuwaski,język dalmatyński,język dari,język dolnoniemiecki,język dolnołużycki,język duński,język dzongkha,język erzja,język estoński,język etruski,język farerski,język fenicki,język fidżyjski,język filipino,język fiński,język francuski,język friulski,język fryzyjski,język fryzyjski saterlandzki,język ful,język ga,język gagauski,język galicyjski,język gaskoński,język gocki,język grenlandzki,język gruziński,język guarani,język gudźarati,język gyyz,język górnołużycki,język haitański,język hausa,język hawajski,język hebrajski,język hiligaynon,język hiszpański,język holenderski,język hupa,język ilokano,język indonezyjski,język inguski,język irlandzki,język islandzki,język istriocki,język jakucki,język japoński,język jawajski,język jaćwieski,język joruba,język kabylski,język kakczikel,język kannada,język karaczajsko-bałkarski,język karakałpacki,język karelski,język kaszubski,język kataloński,język kazachski,język kałmucki,język keczua,język khmerski,język kirgiski,język klingoński,język komi,język komi-jaźwiński,język komi-permiacki,język komi-zyriański,język konkani,język koptyjski,język koreański,język kornijski,język korsykański,język kri,język krymskotatarski,język kumycki,język kurdyjski,język kurmandżi,język ladyński,język langwedocki,język laotański,język lazyjski,język lezgiński,język liguryjski,język limburski,język litewski,język lombardzki,język luksemburski,język luo,język macedoński,język malajalam,język malajski,język malediwski,język malgaski,język maltański,język manx,język maoryski,język maryjski,język mazanderański,język mikmak,język minnan,język moksza,język mongolski,język motu,język mołdawski,język nahuatl,język nauruański,język nawaho,język neapolitański,język neo,język nepalski,język niemiecki,język normandzki,język norweski (bokmål),język norweski (nynorsk),język nowogrecki,język orija,język ormiański,język oromo,język osetyjski,język osmańsko-turecki,język pali,język paszto,język pendżabski,język pensylwański,język perski,język piemoncki,język pikardyjski,język pirahã,język plautdietsch,język polski,język portugalski,język połabski,język pragermański,język prowansalski,język pruski,język północnofryzyjski,język północnolapoński,język rarotonga,język romansz,język romski,język rosyjski,język rumuński,język rundi,język rusiński,język russenorsk,język sardyński,język serbski,język serbsko-chorwacki,język shelta,język shona,język sindhi,język sko,język skolt,język somalijski,język staro-cerkiewno-słowiański,język staro-wysoko-niemiecki,język staroangielski,język staroegipski,język starofrancuski,język starogrecki,język staroirlandzki,język staronordyjski,język staroormiański,język staroruski,język suahili,język sumeryjski,język sundajski,język susu,język sycylijski,język syngaleski,język szerpa,język szkocki,język szkocki gaelicki,język szorski,język szwabski,język szwedzki,język słowacki,język słoweński,język słowiński,język tabasarański,język tadżycki,język tagalski,język tahitański,język tajski,język tamaszek,język tamazight,język tamilski,język tashelhiyt,język tatarski,język telugu,język tigrinia,język tonga,język turecki,język turkmeński,język tuvalu,język tuwiński,język twi,język tybetański,język udmurcki,język ujgurski,język ukraiński,język urdu,język uwea,język uzbecki,język võro,język walijski,język waloński,język warajski,język wczesny nowoangielski,język wenecki,język wepski,język wietnamski,język wilamowski,język wolof,język wysokoislandzki,język węgierski,język włoski,język xhosa,język yupik środkowy,język zachodnioflamandzki,język zarfatit,język zelandzki,język zulu,język łaciński,język łatgalski,język łotewski,język średnio-dolno-niemiecki,język średnio-wysoko-niemiecki,język średnioangielski,język żmudzki,Lingua Franca Nova,quenya,romániço,wenedyk".split(','))
    _WIKI_LANGUAGES_SHORT = set(u"nagłówek języka,termin obcy w języku polskim,termin obcy w języku łacińskim,dżuhuri,esperanto,ewe,hindi,ido,interlingua,inuktitut,kaszmirski,marathi,newarski,sorani,zazaki,ladino,lingala,novial,papiamento,pitjantjatjara,sanskryt,slovio,sranan tongo,tetum,tok pisin,tupinambá,użycie międzynarodowe,volapük,znak chiński,brithenig,esperanto (morfem),jidysz,jèrriais,!Xóõ,a-pucikwar,abazyński,abchaski,abenaki,adygejski,afar,afrykanerski,ajmara,akadyjski,aklanon,alabama,albański,alemański,aleucki,ama,amharski,angielski,arabski,aragoński,aramejski,arapaho,arczyński,arumuński,assamski,asturyjski,awarski,azerski,bambara,banjumasański,baskijski,baszkirski,bawarski,beludżi,bengalski,białoruski,białoruski (taraszkiewica),birmański,bislama,boloński,bośniacki,bretoński,bugijski,bułgarski,cebuano,chakaski,chantyjski (kazymski),chantyjski (surgucki),chantyjski (szuryszkarski),chantyjski (wachowski),chickasaw,chiński standardowy,chorwacki,czagatajski,czamorro,czarnogórski,czeczeński,czeski,czirokeski,czuwaski,dalmatyński,dari,dolnoniemiecki,dolnołużycki,duński,dzongkha,erzja,estoński,etruski,farerski,fenicki,fidżyjski,filipino,fiński,francuski,friulski,fryzyjski,fryzyjski saterlandzki,ful,ga,gagauski,galicyjski,gaskoński,gocki,grenlandzki,gruziński,guarani,gudźarati,gyyz,górnołużycki,haitański,hausa,hawajski,hebrajski,hiligaynon,hiszpański,holenderski,hupa,ilokano,indonezyjski,inguski,irlandzki,islandzki,istriocki,jakucki,japoński,jawajski,jaćwieski,joruba,kabylski,kakczikel,kannada,karaczajsko-bałkarski,karakałpacki,karelski,kaszubski,kataloński,kazachski,kałmucki,keczua,khmerski,kirgiski,klingoński,komi,komi-jaźwiński,komi-permiacki,komi-zyriański,konkani,koptyjski,koreański,kornijski,korsykański,kri,krymskotatarski,kumycki,kurdyjski,kurmandżi,ladyński,langwedocki,laotański,lazyjski,lezgiński,liguryjski,limburski,litewski,lombardzki,luksemburski,luo,macedoński,malajalam,malajski,malediwski,malgaski,maltański,manx,maoryski,maryjski,mazanderański,mikmak,minnan,moksza,mongolski,motu,mołdawski,nahuatl,nauruański,nawaho,neapolitański,neo,nepalski,niemiecki,normandzki,norweski (bokmål),norweski (nynorsk),nowogrecki,orija,ormiański,oromo,osetyjski,osmańsko-turecki,pali,paszto,pendżabski,pensylwański,perski,piemoncki,pikardyjski,pirahã,plautdietsch,polski,portugalski,połabski,pragermański,prowansalski,pruski,północnofryzyjski,północnolapoński,rarotonga,romansz,romski,rosyjski,rumuński,rundi,rusiński,russenorsk,sardyński,serbski,serbsko-chorwacki,shelta,shona,sindhi,sko,skolt,somalijski,staro-cerkiewno-słowiański,staro-wysoko-niemiecki,staroangielski,staroegipski,starofrancuski,starogrecki,staroirlandzki,staronordyjski,staroormiański,staroruski,suahili,sumeryjski,sundajski,susu,sycylijski,syngaleski,szerpa,szkocki,szkocki gaelicki,szorski,szwabski,szwedzki,słowacki,słoweński,słowiński,tabasarański,tadżycki,tagalski,tahitański,tajski,tamaszek,tamazight,tamilski,tashelhiyt,tatarski,telugu,tigrinia,tonga,turecki,turkmeński,tuvalu,tuwiński,twi,tybetański,udmurcki,ujgurski,ukraiński,urdu,uwea,uzbecki,võro,walijski,waloński,warajski,wczesny nowoangielski,wenecki,wepski,wietnamski,wilamowski,wolof,wysokoislandzki,węgierski,włoski,xhosa,yupik środkowy,zachodnioflamandzki,zarfatit,zelandzki,zulu,łaciński,łatgalski,łotewski,średnio-dolno-niemiecki,średnio-wysoko-niemiecki,średnioangielski,żmudzki,Lingua Franca Nova,quenya,romániço,wenedyk".split(','))
    
    def __init__(self, path):
        """Opens wiktionary dump.
        
        Args:
            path: A string representing path to wiktionary dump.
            language: A string in polish representing language of dictionary.
        """
        self.f = open(path, 'r')
    
    def __iter__(self):
        return self.__entries()
    
    def __entries(self):
        """A generator yielding entries in language."""
        generator = self.__parse()
        for page in generator:
            for e in page.entries:
                if e.language not in self._WIKI_LANGUAGES:
                    # print >> sys.stderr, 'unknown language: ' + e.language + ' word: ' + e.word
                    pass
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

def unique(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

if __name__ == '__main__':
    WIKI_LANGUAGES_ENGLISH = {u'angielski':u'english', u'polski':u'polish', u'niemiecki':u'german', u'francuski':u'french', u'hiszpański':u'spanish',
                              u'szwedzki':u'swedish', u'włoski':u'italian', u'czeski':u'czech', u'arabski':u'arabic', u'łaciński':u'latin', u'nowogrecki':u'moderngreek',
                              u'rosyjski':u'russian', u'słowacki':u'slovak', u'ukraiński':u'ukrainian', u'holenderski':u'dutch', u'turecki':u'turkish',
                              u'duński':u'danish', u'fiński':u'finnish', u'język angielski':u'english', u'język polski':u'polish', u'język niemiecki':u'german', u'język francuski':u'french',
                              u'język hiszpański':u'spanish', u'interlingua':u'interlingua', u'esperanto':u'esperanto', u'jidysz':u'yiddish', u'język szwedzki':u'swedish',
                              u'język włoski':u'italian', u'język czeski':u'czech', u'język arabski':u'arabic', u'język łaciński':u'latin', u'język nowogrecki':u'moderngreek',
                              u'język rosyjski':u'russian', u'język słowacki':u'slovak', u'język ukraiński':u'ukrainian', u'język holenderski':u'dutch', u'język turecki':u'turkish',
                              u'język duński':u'danish', u'język fiński':u'finnish', u'bułgarski':u'bulgarian', u'język bułgarski':u'bulgarian',
                              u'język portugalski':u'portuguese', u'portugalski':u'portuguese', u'język norweski (bokmål)':u'norwegian', u'norweski (bokmål)':u'norwegian'
                              , u'język litewski':u'lithuanian', u'język łotewski':u'latvian', u'język estoński':u'estonian',
                              u'litewski':u'lithuanian', u'łotewski':u'latvian', u'estoński':u'estonian', u'chorwacki':u'croatian', u'język chorwacki':u'croatian',
                              u'gruziński':u'georgian', u'język gruziński':u'georgian', u'kataloński':u'catalan', u'język kataloński':u'catalan', u'japoński':u'japanese', 
                              u'język japoński':u'japanese', u'koreański':u'korean', u'język koreański':u'korean', u'węgierski':u'hungarian', u'język węgierski':u'hungarian'}
    dire = 'dictionaries/'
    locale.setlocale(locale.LC_ALL, "")
    
    path = sys.argv[1]
    w = PLWiktionaryToDictionary(path)

    import cPickle
    try:
        f = open('to_polish.pkl')
        to_polish = cPickle.load(f)
        f = open('polish_to.pkl')
        polish_to = cPickle.load(f)
        f = open('zobtlum.pkl')
        zobtlum = cPickle.load(f)
    except IOError:
        to_polish = collections.defaultdict(dict)
        polish_to = collections.defaultdict(dict)
        
        zobtlum = collections.defaultdict(list)
        
        
        
        for e in w:
            if e.language == u'język polski':
                for l, t in e.translations:
                    #polish_to[l].append('%s - %s' % (e.word, ' | '.join(t)))
                    polish_to[l][e.word] = t
                    
                if hasattr(e, 'zobtlum'):
                    zobtlum[e.word] = e.zobtlum
                        
            else:
                if hasattr(e, 'gender') and (e.language == u'język niemiecki' or e.language == u'język francuski'):
                    gender = ' '
                    if u'męski' in e.gender:
                        gender += 'm'
                    if u'żeński' in e.gender:
                        gender += 'f'
                    if u'nijaki' in e.gender:
                        gender += 'n'
                              
                    #to_polish[e.language].append('%s%s - %s' % (e.word, gender, ' | '.join(unique(e.meanings))))
                    to_polish[e.language][e.word+gender] = unique(e.meanings)
                else:
                    #to_polish[e.language].append('%s - %s' % (e.word, ' | '.join(unique(e.meanings))))
                    to_polish[e.language][e.word] = unique(e.meanings)

    import cPickle
    f = open('to_polish.pkl', 'w')
    cPickle.dump(to_polish, f, protocol=-1)
    f = open('polish_to.pkl', 'w')
    cPickle.dump(polish_to, f, protocol=-1)
    f = open('zobtlum.pkl', 'w')
    cPickle.dump(zobtlum, f, protocol=-1)

    for k in to_polish.keys():
        if k not in WIKI_LANGUAGES_ENGLISH:
            continue 
        f = open(dire + WIKI_LANGUAGES_ENGLISH[k] + '_polish.txt', 'w')
        for s in sorted(to_polish[k], cmp=locale.strcoll):
            f.write('%s - %s\n' % (s, ' | '.join(unique(to_polish[k][s]))))
        f.close()
        
    print 'Polish to: '
    
    for k,v in zobtlum.iteritems():
        print k, v
        for k2, v2 in polish_to.iteritems():
            for zob in v:
                if zob in v2:
                    if k not in v2:
                        v2[k]=[]
                    v2[k].extend(v2[zob])
    
    for k in polish_to.keys():
        if k not in w._WIKI_LANGUAGES_SHORT:
            # print >> sys.stderr, 'unknown language Polish to: ' + k + ' word: ' + ','.join(polish_to[k])
            pass
        print k
        if k not in WIKI_LANGUAGES_ENGLISH:
            continue 
        f = open(dire + 'polish_' + WIKI_LANGUAGES_ENGLISH[k] + '.txt', 'w')
        for s in sorted(polish_to[k], cmp=locale.strcoll):
            f.write('%s - %s\n' % (s, ' | '.join(unique(polish_to[k][s]))))
        f.close()
