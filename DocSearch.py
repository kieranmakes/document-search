import re
import numpy as np
import math








class InvertedIndex:

    def __init__(self, ds, docsList):
        self.__index = {}
        self.__ds = ds
        self.__docsList = docsList
        self.__createInvertedIndex()

    def __repr__(self):
        return str(self.__index)


    # outputs the document ids and the frequencies for each term in the query
    # for every document that contains all terms
    # example output:
    # [{'high': [{'docId': 39, 'frequency': 1}, {'docId': 2021, 'frequency': 1}]},
    #  {'levels': [{'docId': 39, 'frequency': 3}, {'docId': 2021, 'frequency': 1}]},
    #  {'growth': [{'docId': 39, 'frequency': 1}, {'docId': 2021, 'frequency': 4}]}]
    def findQuery(self, query):
        queryOccurrences = self.__findTerm(query)
        if len(query.split(" ")) <= 1: return [self.__findTerm(query)]
        # find occurrences that contain all terms in the query
        return self.__retrieveRelevantOccurrencesFromQuery(query)




        # arr = [for termOccurrence in termOccurrences: termOccurrence["docId"]]


    # will return the occurrences with the doc ids and frequency for each of the
    # terms for each doc id but only for the docs that contain all terms
    def __retrieveRelevantOccurrencesFromQuery(self, query):
        # gets each of the occurrences for each term in the query and puts into a 2d array with each inner array
        # dictionaries for each occurrence of that term. dictionary contains docId and frequency
        queryTerms = query.split(" ")
        allOccurrences = [[termOccurrences for termOccurrences in self.__findTerm(term)[term]] for term in queryTerms]

        docIdsForAllTerms = []
        docIdsThatContainAllTerms = []

        # puts all the doc ids into a single array
        for i in range(0, len(allOccurrences)):
            for j in range(0, len(allOccurrences[i])):
                # print(allOccurrences[i][j])
                docIdsForAllTerms.append(allOccurrences[i][j].docId)
        # removes any docIds that dont appear exactly the same number of times as there are terms in full query
        # and puts the docIds of the docs that contain all of the terms into this variable
        docIdsThatContainAllTerms = list(set([duplicateDocId for duplicateDocId in docIdsForAllTerms
                                              if docIdsForAllTerms.count(duplicateDocId) == len(allOccurrences)]))
        # go through allOccurrences' each termOccurrences and then through it's docIds checking it is in docIdsThatContainAllTerms
        # if it's docId is in docIdsThatContainAllTerms, that term occurrence should get appended to the relevantOccurrences list
        relevantOccurrences = []
        for i in range(0, len(allOccurrences)):
            relevantOccurrences.append({queryTerms[i]: []})
            for j in range(0, len(allOccurrences[i])):
                if allOccurrences[i][j].docId in docIdsThatContainAllTerms:
                    relevantOccurrences[i][queryTerms[i]].append(allOccurrences[i][j])

        return relevantOccurrences











    def __findTerm(self, term):
        return {term: self.__index[term] for term in term.split(' ') if term in self.__index}


    def __createInvertedIndex(self):
        for i in range(0, len(self.__docsList)):
            self.__indexDocument({'id': i, 'text': self.__docsList[i]})


    def __indexDocument(self, document):

        # Remove white space and punctuation from the text.
        terms = re.sub(r'[^\w\s]', '', document['text']).replace("\n",'').replace("\t",' ').split(' ')
        termOccurrenceDictionary = {}
        # Dictionary with each term and the frequency it appears in the text.
        for term in terms:
            termOccurrenceDictionary[term] = TermOccurrence(document['id'])

        # inverted index gets updated
        updateDictionary = {key: [termOccurrence] if key not in self.__index else self.__index[key] + [termOccurrence]
                       for (key, termOccurrence) in termOccurrenceDictionary.items()}
        self.__index.update(updateDictionary)
        # Add the document into the datastore
        self.__ds.append(document)
        return document






class DataStore:

    def __init__(self):
        self.__ds = dict()

    def __repr__(self):
        return str(self.__dict__)

    def retrieve(self, id):
        return self.__ds.get(id, None)

    def append(self, document):
        return self.__ds.update({document['id']: document})

    def delete(self, document):
        return self.__ds.pop(document['id'], None)


class TermOccurrence:

    def __init__(self, docId):
        self.docId = docId


    def __repr__(self):
        return str(self.__dict__)





class DocumentSearching:

    def __init__(self, documentsFile, queriesFile):
        self.__docsList = self.__fileToListByNewLine(documentsFile)
        self.__queriesList = self.__fileToListByNewLine(queriesFile)
        self.__dictionaryOfUniqueWords = self.__createDictOfUniqueWords()
        self.__ds = DataStore()
        self.__invertedIndex = InvertedIndex(ds=self.__ds, docsList=self.__docsList)
        self.__docVectorsCache = {}

    def __fileToListByNewLine(self, filePath):
        file = open(filePath, "r")
        fileAsList = []
        for line in file:
            # appends term to the docs list without any trailing characters and excessive white space
            fileAsList.append(line.replace("\n", '').replace("\t", ' ').replace("\r", '').replace("\f", ''))
        file.close()
        return fileAsList

    # returns a list of unique words found in the docs
    def __createDictOfUniqueWords(self):
        # puts all the words from all the docs into one list
        allTheWordsInTheDocs = []
        for doc in self.__docsList:
            currentDoc = doc.split(" ")
            for word in currentDoc:
                allTheWordsInTheDocs.append(word)
        #print("all the words from the docs: \t\t" + str(allTheWordsInTheDocs))

        # removes any duplicates of words
        uniqueWords = sorted(set(allTheWordsInTheDocs))
        if '' in uniqueWords: uniqueWords.remove('')
        if ',' in uniqueWords: print("aghhh")
        #print("all the unique words from the docs: \t\t" + str(uniqueWords))
        return uniqueWords


    def __createVectorForDocument(self, document):
        vector = [0 for i in range(len(self.__dictionaryOfUniqueWords))]
        documentArr = document.split(" ")
        if '' in documentArr: documentArr.remove('')
        for word in documentArr:
            i = self.__dictionaryOfUniqueWords.index(word)
            vector[i] += 1
        #print("document \t" + str(vector))
        return np.array(vector)



    # example queryOccurrence argument:
    # [{'high': [{'docId': 39, 'frequency': 1}, {'docId': 2021, 'frequency': 1}]},
    #  {'levels': [{'docId': 39, 'frequency': 3}, {'docId': 2021, 'frequency': 1}]},
    #  {'growth': [{'docId': 39, 'frequency': 1}, {'docId': 2021, 'frequency': 4}]}]
    def __createVectorForQuery(self, queryOccurrence, docId):
        vector = [0 for i in range(len(self.__dictionaryOfUniqueWords))]

        for i in range(0, len(queryOccurrence)):
            term = list(queryOccurrence[i].keys())[0]
            index = self.__dictionaryOfUniqueWords.index(term)
            vector[index] = 1

        #print("query \t\t" + str(vector))
        return np.array(vector)


    # calculates the angle between the two vectors x and y
    def __calculateAngle(self, x, y):
        normX = np.linalg.norm(x)
        normY = np.linalg.norm(y)
        cosTheta = np.dot(x, y) / (normX * normY)
        theta = math.degrees(math.acos(cosTheta))
        return theta




    def runDocumentSearch(self):

        relevantDocuments = []
        relevantDocumentsStr = ""
        documentVector = []
        queryVector = []
        docsAndAngles2dList = []

        print("Words in dictionary:  {}".format(len(self.__dictionaryOfUniqueWords)))
        for query in self.__queriesList:
            print("Query:  {}".format(query))
            # find all the documents that contain all the words in the query
            # and then +1 to it to make it an id and then put it into a string to be printed
            relevantTermsData = self.__invertedIndex.findQuery(query)
            relevantDocIds = [termOccurrences.docId for termOccurrences in relevantTermsData[0][query.split(" ")[0]]]
            print("Relevant documents: " + str([docId +1 for docId in relevantDocIds])[1:][:-1].replace(',',''))

            # for every doc that is relevant to the query create a vector and then
            # find the angle between the query vector and the current document vector
            for docId in relevantDocIds:
                if docId not in self.__docVectorsCache: # make vector if not in cache
                    self.__docVectorsCache[docId] = self.__createVectorForDocument(self.__docsList[docId])
                    documentVector = self.__docVectorsCache[docId]
                else: # use cached vector if there
                    documentVector = self.__docVectorsCache[docId]
                # create vector for query
                queryVector = self.__createVectorForQuery(relevantTermsData, docId)

                # append the docId+1 to a dictionary with it's value being the angle between document and query vectors
                docsAndAngles2dList.append([str(docId + 1),format(
                    round(self.__calculateAngle(documentVector, queryVector), 5), '.5f')])
                # sorts the dictionary by the values
            docsAndAngles2dList = sorted(docsAndAngles2dList,key=lambda x: x[1])
            line = ""
            for i in range(0, len(docsAndAngles2dList)):
                for j in range(0, len(docsAndAngles2dList[i])):
                    line = line + " " + docsAndAngles2dList[i][j]
                print(line[1:])
                line = ""
            docsAndAngles2dList = []
















def main():
    documentSearching = DocumentSearching("docs.txt", "queries.txt")
    documentSearching.runDocumentSearch()


main()
