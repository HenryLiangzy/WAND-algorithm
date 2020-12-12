class Term(object):

    def __init__(self, term, post_list):

        self.name = term
        self.doc_list, self.score_list = list(), list()
        self.cursor = 0

        for doc_id, score in post_list:
            self.doc_list.append(doc_id)
            self.score_list.append(score)

        self.ub = max(self.score_list)
        self.did = self.doc_list[self.cursor]

    def next_cursor(self):
        if self.is_out(self.cursor+1):
            return False
        else:
            self.cursor += 1
            self.did = self.doc_list[self.cursor]

            return True

    def skip_to(self, did):
        while self.did < did:
            res = self.next_cursor()
            if not res:
                return False

        return True

    def get_did(self):
        return self.did

    def get_ub(self):
        return self.ub

    def get_score(self):
        return self.score_list[self.cursor]

    def is_out(self, index):
        return index >= len(self.doc_list)

    def __str__(self):
        name = 'Term: '+self.name+'\n'
        doc_list = 'Doc_list: '+str(self.doc_list)+'\n'
        score_list = 'Score_list: '+str(self.score_list)+'\n'
        rest = 'Cursor: {}, Did: {}, Ub: {}\n'.format(self.cursor, self.did, self.ub)

        return name+doc_list+score_list+rest
    #__repr__ = __str__


def WAND_Algo(query_terms, top_k, inverted_index):

    evaluate_time = 0
    
    # load the posting list of query term from inverted index
    term_record = list()
    for term in query_terms:
        term_record.append(Term(term, inverted_index[term]))

    threshold = -1
    ans = list()

    while term_record:

        # sorted the term list by the Did
        term_record = sorted(term_record, key=lambda x: x.get_did())

        score_limit = 0
        pivot_index = 0

        # step 10
        # find the pivot term
        for index in range(len(term_record)):
            temp_s_limit = score_limit + term_record[index].get_ub()

            if temp_s_limit > threshold:
                pivot_index = index
                break

            # if loop all the term still not found the pivot term
            if index+1 == len(term_record):
                return ans, evaluate_time

            score_limit = temp_s_limit

        # step 20
        # if the first term have same did as pivot term did
        if term_record[0].get_did() == term_record[pivot_index].get_did():
            s = 0
            Did = term_record[pivot_index].get_did()
            evaluate_time += 1

            # sum the score
            term_record_copy = term_record.copy()
            for term in term_record_copy:
                if term.get_did() == Did:
                    s  = s + term.get_score()
                    if not term.next_cursor():
                        term_record.remove(term)

            # update the threshold
            if s > threshold:
                ans.append((s, Did))

                if len(ans) > top_k:
                    ans = sorted(ans, key=lambda x: x[0], reverse=True)
                    ans.pop()

                    threshold = ans[-1][0]
        
        # if the first term not same as the pivot term did
        else:
            new_record = list()
            for i in range(0, len(term_record)):
                if term_record[i].skip_to(term_record[pivot_index].get_did()):
                    new_record.append(term_record[i])
            
            term_record = new_record

    if ans:
        ans = sorted(ans, key=lambda x: (x[0], -x[1]), reverse=True)

    return ans, evaluate_time