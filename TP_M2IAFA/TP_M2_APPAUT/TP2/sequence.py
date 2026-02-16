import sys
import warnings


class LabelDictionary(dict):
    """This class implements a dictionary of labels. Labels as mapped to
    integers, and it is efficient to retrieve the label name from its
    integer representation, and vice-versa."""

    def __init__(self, label_names=[]):
        super().__init__()
        self.names = []
        for name in label_names:
            self.add(name)

    def add(self, name):
        label_id = len(self.names)
        if name in self:
            warnings.warn('Ignoring duplicated label ' + name)
        self[name] = label_id
        self.names.append(name)
        return label_id

    def get_label_name(self, label_id):
        return self.names[label_id]

    def get_label_id(self, name):
        return self[name]


class Sequence(object):

    def __init__(self, sequence_list, x, y, nr):
        self.x = x
        self.y = y
        self.nr = nr
        self.sequence_list = sequence_list

    def size(self):
        """Returns the size of the sequence."""
        return len(self.x)

    def __len__(self):
        return len(self.x)

    def copy_sequence(self):
        """Performs a deep copy of the sequence"""
        s = Sequence(self.sequence_list, self.x[:], self.y[:], self.nr)
        return s

    def update_from_sequence(self, new_y):
        """Returns a new sequence equal to the previous but with y set to newy"""
        s = Sequence(self.sequence_list, self.x, new_y, self.nr)
        return s

    def __str__(self):
        rep = ""
        for i, xi in enumerate(self.x):
            yi = self.y[i]
            rep += "%s/%s " % (self.sequence_list.x_dict.get_label_name(xi),
                               self.sequence_list.y_dict.get_label_name(yi))
        return rep

    def __repr__(self):
        rep = ""
        for i, xi in enumerate(self.x):
            yi = self.y[i]
            rep += "%s/%s " % (self.sequence_list.x_dict.get_label_name(xi),
                               self.sequence_list.y_dict.get_label_name(yi))
        return rep


class _SequenceIterator():

    def __init__(self, seq):
        self.seq = seq
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos >= len(self.seq):
            raise StopIteration
        r = self.seq[self.pos]
        self.pos += 1
        return r


class SequenceList(object):

    def __init__(self, x_dict, y_dict):
        self.x_dict = x_dict
        self.y_dict = y_dict
        self.seq_list = []

    def __str__(self):
        return str(self.seq_list)

    def __repr__(self):
        return repr(self.seq_list)

    def __len__(self):
        return len(self.seq_list)

    def __getitem__(self, ix):
        return self.seq_list[ix]

    def __iter__(self):
        return _SequenceIterator(self)

    def size(self):
        """Returns the number of sequences in the list."""
        return len(self.seq_list)

    def get_num_tokens(self):
        """Returns the number of tokens in the sequence list, that is, the
        sum of the length of the sequences."""
        return sum([seq.size() for seq in self.seq_list])

    def add_sequence(self, x, y):
        """Add a sequence to the list, where x is the sequence of
        observations, and y is the sequence of states."""
        num_seqs = len(self.seq_list)
        x_ids = [self.x_dict.get_label_id(name) for name in x]
        y_ids = [self.y_dict.get_label_id(name) for name in y]
        self.seq_list.append(Sequence(self, x_ids, y_ids, num_seqs))

    def save(self, file):
        seq_fn = open(file, "w")
        for seq in self.seq_list:
            txt = ""
            for pos, word in enumerate(seq.x):
                txt += "%i:%i\t" % (word, seq.y[pos])
            seq_fn.write(txt.strip() + "\n")
        seq_fn.close()

    def load(self, file):
        seq_fn = open(file, "r")
        seq_list = []
        for line in seq_fn:
            seq_x = []
            seq_y = []
            entries = line.strip().split("\t")
            for entry in entries:
                x, y = entry.split(":")
                seq_x.append(int(x))
                seq_y.append(int(y))
            self.add_sequence(seq_x, seq_y)
        seq_fn.close()


class SimpleSequence:

    def __init__(self):
        # Observation set.
        self.x_dict = LabelDictionary(['walk', 'shop', 'clean', 'tennis'])

        # State set.
        self.y_dict = LabelDictionary(['rainy', 'sunny'])

        # Generate training sequences.
        train_sequences = SequenceList(self.x_dict, self.y_dict)
        train_sequences.add_sequence(['walk', 'walk', 'shop', 'clean'], ['rainy', 'sunny', 'sunny', 'sunny'])
        train_sequences.add_sequence(['walk', 'walk', 'shop', 'clean'], ['rainy', 'rainy', 'rainy', 'sunny'])
        train_sequences.add_sequence(['walk', 'shop', 'shop', 'clean'], ['sunny', 'sunny', 'sunny', 'sunny'])

        # Generate test sequences.
        test_sequences = SequenceList(self.x_dict, self.y_dict)
        test_sequences.add_sequence(['walk', 'walk', 'shop', 'clean'], ['rainy', 'sunny', 'sunny', 'sunny'])
        test_sequences.add_sequence(['clean', 'walk', 'tennis', 'walk'], ['sunny', 'sunny', 'sunny', 'sunny'])

        self.train = train_sequences
        self.test = test_sequences