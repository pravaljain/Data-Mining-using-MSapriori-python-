import sys
import operator

def read_input():
    class Error(Exception):
        pass
    try:
        #f=open('data-1.txt','r'); #reading input file in read-only mode
        f = open('data-2.txt', 'r');  # reading input file in read-only mode
        global input_data;
        input_data=[]
        for line in f:
            line=line.replace("{","")#converting transaction from input file into series of numbers
            line=line.replace("}", "")
            line = line.replace("\n", "")
            line_split=line.split(", ")
            line_split=[int(i) for i in line_split]
            input_data.append(line_split)

    except Error:
        print ('E')

def read_mis():
    class Error(Exception):
        pass
    try:
        #f=open('para1-2.txt','r'); #reading parameters file in read-only mode
        f = open('para2-2.txt', 'r');  # reading parameters file in read-only mode
        global mis_data;
        mis_data={}
        for line in f:
            if "cannot_be_together" in line:#separating the cannot_be_together clause from the parameter file as a global variable
                line_split = line.split(':')
                global cons1;
                cons1=line_split[1]
                cons1=cons1.split('}, {')
                cons1list = []
                for item in cons1:
                    item=item.replace(' {','');
                    item=item.replace('}', '');
                    item = item.replace('\n', '');
                    itemsplitted=item.split(', ')
                    itemsplitted = [int(i) for i in itemsplitted]
                    cons1list.append(itemsplitted)
                cons1=cons1list;
            elif "must-have" in line:#separating the must_have clause from the parameter file as a global variable
                line=line.replace('\n','')
                line_split = line.split(':')
                global cons2
                cons2=line_split[1]
                cons2=cons2.split(' or ')
                cons2=[int(i.strip()) for i in cons2]
                #print (cons2)
            elif "SDC" in line:#separately storing the SDC value as a global variable
                line_split=line.split('=')
                global SDC
                SDC=line_split[1].strip()
                #print ('SDC',SDC)
            else:
                global mis;# storing the items with their respective mis as a global variable
                line_split=line.split('=')
                mis=(line_split[0].replace('MIS(','')).replace(')', '');
                #mis = mis.replace(')', '');
                global mis_value
                mis_value=line_split[1].strip()
                mis_data[int(mis.strip())]=float(mis_value);

    except Error:
        print ('E')

#to sort the items based on their mis values
def sortitems():
    global M;
    k=0;
    M = sorted(mis_data.items(), key=operator.itemgetter(1));

#function that performs the intial pass of the MSapriori algorithm
def init_pass(M,T):
    n=len(T)
    L=[];
    support_count={};
    support={}
    v=-1;
    for item in M:
        key,value=item
        support_count[key]=0
        for k in T:
            if key in k:
                support_count[key]=support_count[key]+1;
        support[key]=support_count[key]/n;
        if v==-1:
            vvalue=mis_data[key];
            v=100;
            if support[key]>=vvalue:
                L.append(key);
        elif support[key]>=vvalue:
            L.append(key);
    return L;

#getting the value of 1-frequent itemset or F1
def getF1(L,T):
    global n;
    n=len(T)
    F1=[]
    support_count={};
    support={}
    v=-1;
    for item in L:
        key=item;
        support_count[key]=0
        for k in T:
            if key in k:
                support_count[key]=support_count[key]+1;
        support[key]=support_count[key]/n;
        vvalue=mis_data[key]
        if support[key]>=vvalue:
            F1.append(key);
    return F1;

#function to generate the level-2 candidate or C2
def level2_cand_gen(L,SDC):
    c2=[];
    for l in L:
        lcount=0;
        for k in input_data:
            if l in k:
                lcount=lcount+1;
        lindex=L.index(l)
        misl=mis_data[l]
        if lcount/n>=misl:
            for h in L[lindex+1:]:
                hcount=0;
                for kh in input_data:
                    if h in kh:
                        hcount=hcount+1;
                if (hcount/n>=misl and (abs(hcount/n-lcount/n)<=float(SDC)) ):
                    overall_cons1 = True;
                    for cons1_items in cons1:
                        go_cons1 = True;
                        for cons1_elements in cons1_items:
                            if cons1_elements in [l,h]:
                                if go_cons1 == False:
                                    overall_cons1 = False
                                else:
                                    go_cons1 = False;
                    if overall_cons1 == True:
                        c2.append([l,h])
    return c2;


# calculate the support count or x.oount of each item or x
def scount(index,dt):
	tee = 0
	for i in dt:
		if index in i:
			tee = tee+1
	return tee

#Function to generate level-k candicates or Ck
def mscandidate_gen(F, sdc):
    sdc=float(sdc)
    C = []
    n = len(input_data)
    #Execution of the join step where the items from Fk-1 are joined to form Ck
    for i in F:
        for j in F:
            if i[0:-1] == j[0:-1] and i[-1] < j[-1] and abs(
                            scount(i[-1], input_data)/n - scount(j[-1], input_data)/n) <= (sdc):
                c = []
                c = i[:]

                c.append(j[-1])
                C.append(c)

    #Execution of the prune step where those items in Ck are pruned whose subsets are not in Fk-1
    for k in C:
        p = C.index(k)
        subset = []
        for i in k:
            jay = []
            pi = k.index(i)
            jay = k[:pi] + k[pi + 1:]
            subset.append(jay)
        for j in subset:
            if k[0] in j or mis_data[k[0]] == mis_data[k[1]]:
                if j not in F:
                    del C[p]
                    break

    return C


#execution of the MSapriori algorithm begins here
read_mis() #reading parameter-file
read_input()#reading input-file
sortitems()#sorting to create M
L=init_pass(M,input_data)#calling the init-pass function to generate L
F1=getF1(L,input_data)#getF1 generates F1 from L
c2=level2_cand_gen(L,SDC)#generating C2
#initializations
C=[]
F=[];
F.append(F1);
freq=[];
tail=[];
#initializations end

for k in range(1,1000,1):
    if not F[k-1]:
        break;
    if k==1:
        C=level2_cand_gen(L,SDC);#generating C2
    else:
        C=mscandidate_gen(F[k-1],SDC);
    clist=[];
    countlist=[];
    tailcountlist=[]
    for cand in C:
        cand_tailcount = 0;
        candcount = 0;
        for t in input_data:

            cf=True;
            for cfloop in cand:
                if cfloop not in t:
                    cf=False;
            if cf==True:
                candcount=candcount+1;
            copy_cand=cand[1:]
            cftail=True;
            for cfloop in copy_cand:
                if cfloop not in t:
                    cftail=False;
            if cftail==True:
                cand_tailcount = cand_tailcount + 1;
        candone=cand[0];
        if ((cand in C) and (candcount/n>=float(mis_data[candone]))):
            overall_cons1 = True;
            for cons1_items in cons1:
                go_cons1 = True;
                for cons1_elements in cons1_items:
                    if cons1_elements in cand:
                        if go_cons1 == False:
                            overall_cons1 = False
                        else:
                            go_cons1 = False;
            if overall_cons1==True:
                clist.append(cand)
                countlist.append(candcount)
                tailcountlist.append(cand_tailcount)

    F.append(clist)
    freq.append(countlist)
    tail.append(tailcountlist)

#printing the output in the given format
print ('-----OUTPUT-----\n\n')
def const_musthave(F):
    go = False;
    kindex=-1;
    for fk in F:
        tot=0;
        kindex=kindex+1;
        if kindex==0:
            print ('Frequent 1-itemsets\n')
            counter=0;
            for fk_element in fk:
                if fk_element in cons2:
                    count_ind=0;
                    for t in input_data:
                        if fk_element in t:
                            count_ind=count_ind+1;
                    counter = counter + 1;
                    print ('\t'+str(count_ind)+' : ['+str(fk_element)+']');
            print('\n\tTotal number of freuqent 1-itemsets = ', counter)
        else:
            text5=''
            text5+=('\nFrequent ' + str(kindex + 1) + '-itemsets\n')
            fkindex=-1;
            counter = 0;
            for fk_itemset in fk:
                fkindex=fkindex+1;
                #checking for the must_have constraint
                go=False;
                for cons2_elements in cons2:
                    if cons2_elements in fk_itemset:
                        go=True;
                #checking for the cannot_be_together constraint
                overall_cons1 = True;
                for cons1_items in cons1:
                    go_cons1 = True;
                    for cons1_elements in cons1_items:
                        if cons1_elements in fk_itemset:
                            if go_cons1 == False:
                                overall_cons1=False
                            else:
                                go_cons1 = False;
                if go==True and overall_cons1==True:
                    #sorting the selected sub-items according to their mis value to maintain total order
                    cand_sort = {};
                    for candele in fk_itemset:
                        cand_sort[candele] = mis_data[candele];
                    cand_sorted = sorted(cand_sort.items(), key=operator.itemgetter(1));
                    fk_itemset_sorted = [];
                    for cand_sorted_elements in cand_sorted:
                        keyb, valueb = cand_sorted_elements
                        fk_itemset_sorted.append(keyb);
                    #sorting ends

                    fk_itemset_str=", ".join(str(x) for x in fk_itemset_sorted)
                    text5 +=('\n\t'+str(freq[kindex - 1][fkindex])+' : ['+ fk_itemset_str+']')
                    text5 +=('\nTailcount = ' + str(tail[kindex - 1][fkindex]))
                    counter = counter + 1;
            if counter>0:
                print (text5);
                print('\n\tTotal number of freuqent ' + str(kindex + 1) + '-itemsets = ', counter)

const_musthave(F);