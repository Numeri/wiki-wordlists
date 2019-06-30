# wiki-wordlists
*Generates Unicode word frequency lists from Wikipedia pages in any language.*  

If you've ever wanted a word frequency list for a given language or subject—whether to start learning a new language, or just out of curiosity—you can finally do so. *wiki-wordlists* lets you extract a list of the top words used in any wiki that allows exporting pages as xml (Wikipedia, for example).  

This allows you to create a word frequency list of the top 1000 words used across the entire English Wikipedia, for example, or the top 300 in the category Mathematics. If you were learning Swedish, you could get the 1000 most used words to start a vocabulary deck (the first 1000 words account for [75–80% of all usage](http://davies-linguistics.byu.edu/ling485/for_class/hispling_final.htm)).  

## Usage

``python wiki-wordlists.py <input file> [number of words]``

The input file should be an xml dump of the set of Wikipedia pages you would like to process. This could be one or more specific pages or categories downloaded from [Wikipedia's Export page](https://en.wikipedia.org/wiki/Special:Export), or the equivalent page in a different language. Alternatively, you could download the xml dump of all the pages in Wikipedia in a certain language, available as [zipped files here](https://dumps.wikimedia.org/backup-index.html). 

 > Warning: The zipped xml dumps of entire Wikipedias are very large! 
 
 An example of using *wiki-wordlists* on the entire English Wikipedia would look like this (if you downloaded the 65gb file!):  
 
     bzip2 -d wikidatawiki-20190620-pages-articles-multistream.xml.bz2
     python wiki-wordlists.py wikidatawiki-20190620-pages-articles-multistream.xml 1000

Do note that the program has never been tested on files that large!
