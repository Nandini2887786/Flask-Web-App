from flask import Flask, render_template, request, redirect, url_for
import itertools
import csv

app = Flask(__name__)

# Apriori Functions (as in your original code)

def apriori_gen(frequent_itemsets, k):
    candidates = []
    len_f = len(frequent_itemsets)
    for i in range(len_f):
        for j in range(i + 1, len_f):
            itemset1 = list(frequent_itemsets[i])
            itemset2 = list(frequent_itemsets[j])
            itemset1.sort()
            itemset2.sort()
            if itemset1[:k - 2] == itemset2[:k - 2]:
                candidate = set(itemset1) | set(itemset2)
                if not has_infrequent_subset(candidate, frequent_itemsets):
                    candidates.append(candidate)
    return candidates

def has_infrequent_subset(candidate, frequent_itemsets):
    for subset in itertools.combinations(candidate, len(candidate) - 1):
        if set(subset) not in frequent_itemsets:
            return True
    return False

def find_frequent_1_itemsets(transactions, min_support):
    item_counts = {}
    for transaction in transactions:
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1
    frequent_itemsets = [{item} for item, count in item_counts.items() if count >= min_support]
    return frequent_itemsets, item_counts

def filter_candidates_by_support(transactions, candidates, min_support):
    candidate_counts = {frozenset(candidate): 0 for candidate in candidates}
    for transaction in transactions:
        transaction_set = set(transaction)
        for candidate in candidates:
            if candidate.issubset(transaction_set):
                candidate_counts[frozenset(candidate)] += 1
    frequent_itemsets = [set(candidate) for candidate, count in candidate_counts.items() if count >= min_support]
    return frequent_itemsets

def apriori(transactions, min_support):
    frequent_itemsets = []
    freq_1_itemsets, _ = find_frequent_1_itemsets(transactions, min_support)
    current_frequent_itemsets = freq_1_itemsets
    k = 2
    while current_frequent_itemsets:
        frequent_itemsets.extend(current_frequent_itemsets)
        candidates = apriori_gen(current_frequent_itemsets, k)
        current_frequent_itemsets = filter_candidates_by_support(transactions, candidates, min_support)
        k += 1
    return frequent_itemsets

def load_transactions(file):
    transactions = []
    file.seek(0)  # Rewind file to the start
    reader = csv.reader(file)
    for row in reader:
        transactions.append(row)
    return transactions


# Flask Routes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        min_support = int(request.form['min_support'])

        # Load transactions and apply apriori algorithm
        transactions = load_transactions(file)
        frequent_itemsets = apriori(transactions, min_support)

        # Prepare results to send to template
        results = [list(itemset) for itemset in frequent_itemsets]
        return render_template('results.html', results=results, min_support=min_support)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
