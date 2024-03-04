def print_cm(self):
    # TO-DO: make it generic
    for i in range(self.distance_bins):
        print(" ")
        headers=['']
        predictions = []
        for k,v in self.map.items():
            headers.append(v)
            pred_class = v
            pred_row = list(self.C[i][k,:])
            predictions.append([pred_class, *pred_row])

        print("Printing confusion matrix from distance d <= {0}".format(self.markers[i]))

        table_C = tabulate(predictions, headers=headers, tablefmt='latex')
        print(table_C)