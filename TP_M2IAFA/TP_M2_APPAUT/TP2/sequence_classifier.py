from log_domain import *


class SequenceClassificationDecoder:
    """ Implements a sequence classification decoder."""

    def __init__(self):
        pass

    # ----------
    # Computes the forward trellis for a given sequence.
    # Receives:
    #
    # Initial scores: (num_states) array
    # Transition scores: (length-1, num_states, num_states) array
    # Final scores: (num_states) array
    # Emission scores: (length, num_states) array
    # ----------
    def run_forward(self, initial_scores, transition_scores, final_scores, emission_scores):
        length = np.size(emission_scores, 0)  # Length of the sequence.
        num_states = np.size(initial_scores)  # Number of states.

        # Forward variables.
        forward = np.zeros([length, num_states]) + logzero()

        # Initialization.
        forward[0, :] = emission_scores[0, :] + initial_scores

        # Forward loop.
        for pos in range(1, length):
            for current_state in range(num_states):
                # Note the fact that multiplication in log domain turns a sum and sum turns a logsum
                forward[pos, current_state] = logsum(forward[pos-1, :] + transition_scores[pos-1, current_state, :])
                forward[pos, current_state] += emission_scores[pos, current_state]

        # Termination.
        log_likelihood = logsum(forward[length-1, :] + final_scores)

        return log_likelihood, forward

    # ----------
    # Computes the backward trellis for a given sequence.
    # Receives:
    #
    # Initial scores: (num_states) array
    # Transition scores: (length-1, num_states, num_states) array
    # Final scores: (num_states) array
    # Emission scores: (length, num_states) array
    # ----------
    def run_backward(self, initial_scores, transition_scores, final_scores, emission_scores):
        length = np.size(emission_scores, 0)  # Length of the sequence.
        num_states = np.size(initial_scores)  # Number of states.

        # Backward variables.
        backward = np.zeros([length, num_states]) + logzero()

        # Initialization.
        backward[length-1, :] = final_scores

        # Backward loop.
        for pos in range(length-2, -1, -1):
            for current_state in range(num_states):
                backward[pos, current_state] = \
                    logsum(backward[pos+1, :] +
                           transition_scores[pos, :, current_state] +
                           emission_scores[pos+1, :])

        # Termination.
        log_likelihood = logsum(backward[0, :] + initial_scores + emission_scores[0, :])

        return log_likelihood, backward

    # ----------
    # Computes the viterbi trellis for a given sequence.
    # Receives:
    #
    # Initial scores: (num_states) array
    # Transition scores: (length-1, num_states, num_states) array
    # Final scores: (num_states) array
    # Emission scores: (length, num_states) array
    # ----------
    def run_viterbi(self, initial_scores, transition_scores, final_scores, emission_scores):

        # ----------
        #

        length = np.size(emission_scores, 0)  # Length of the sequence.
        num_states = np.size(initial_scores)  # Number of states.

        # Variables storing the Viterbi scores.
        viterbi_scores = np.zeros([length, num_states]) + logzero()

        # Variables storing the paths to backtrack.
        viterbi_paths = -np.ones([length, num_states], dtype=int)

        # Most likely sequence.
        best_path = -np.ones(length, dtype=int)

        #  Initialize the viterbi scores: viterbi(1, c_k )
        viterbi_scores[0, :] = emission_scores[0, :] + initial_scores

        # viterbi loop.
        for pos in range(1, length):
            for current_state in range(num_states):
                # viterbi(i, c_k)
                viterbi_scores[pos, current_state] = \
                    np.max(viterbi_scores[pos - 1, :] + transition_scores[pos - 1, current_state, :])
                viterbi_scores[pos, current_state] += emission_scores[pos, current_state]
                # backtrack(i, c_k)
                viterbi_paths[pos, current_state] = \
                    np.argmax(viterbi_scores[pos - 1, :] + transition_scores[pos - 1, current_state, :])

        # Termination: viterbi(N + 1, stop)
        best_score = np.max(viterbi_scores[length - 1, :] + final_scores)
        # backtrack(N + 1, stop)
        best_path[length - 1] = np.argmax(viterbi_scores[length - 1, :] + final_scores)

        # backtrack.
        for pos in range(length - 2, -1, -1):
            best_path[pos] = viterbi_paths[pos + 1, best_path[pos + 1]]
        return best_path, best_score


    def run_forward_backward(self, initial_scores, transition_scores, final_scores, emission_scores):
        log_likelihood, forward = self.run_forward(initial_scores, transition_scores, final_scores, emission_scores)
        print('Log-Likelihood =', log_likelihood)

        log_likelihood, backward = self.run_backward(initial_scores, transition_scores, final_scores, emission_scores)
        print('Log-Likelihood =', log_likelihood)

        return forward, backward


class SequenceClassifier:
    """ Implements an abstract sequence classifier."""

    def __init__(self, observation_labels, state_labels):
        """Initialize a sequence classifier. observation_labels and
        state_labels are the sets of observations and states, respectively.
        They must be LabelDictionary objects."""

        self.decoder = SequenceClassificationDecoder()
        self.observation_labels = observation_labels
        self.state_labels = state_labels
        self.trained = False

    def get_num_states(self):
        """ Return the number of states."""
        return len(self.state_labels)

    def get_num_observations(self):
        """ Return the number of observations (e.g. word types)."""
        return len(self.observation_labels)

    def train_supervised(self, sequence_list):
        """ Train a classifier in a supervised setting."""
        raise NotImplementedError

    def compute_scores(self, sequence):
        """ Compute emission and transition scores for the decoder."""
        raise NotImplementedError

    def compute_output_score(self, states, initial_scores, transition_scores,
                             final_scores, emission_scores):
        length = np.size(emission_scores, 0)  # Length of the sequence.
        score = 0.0
        score += initial_scores[states[0]]
        for pos in range(length):
            score += emission_scores[pos, states[pos]]
            if pos > 0:
                score += transition_scores[pos-1, states[pos], states[pos-1]]
        score += final_scores[states[length-1]]
        return score

    def compute_posteriors(self, initial_scores, transition_scores,
                           final_scores, emission_scores):
        """Compute the state and transition posteriors:
        - The state posteriors are the probability of each state
        occurring at each position given the sequence of observations.
        - The transition posteriors are the joint probability of two states
        in consecutive positions given the sequence of observations.
        Both quantities are computed via the forward-backward algorithm."""

        length = np.size(emission_scores, 0)  # Length of the sequence.
        num_states = np.size(emission_scores, 1)  # Number of states.

        # Run the forward algorithm.
        log_likelihood, forward = self.decoder.run_forward(initial_scores,
                                                           transition_scores,
                                                           final_scores,
                                                           emission_scores)

        # Run the backward algorithm.
        log_likelihood, backward = self.decoder.run_backward(initial_scores,
                                                             transition_scores,
                                                             final_scores,
                                                             emission_scores)

        # Multiply the forward and backward variables and divide by the
        # likelihood to obtain the state posteriors (sum/subtract in log-space).
        # Note that log_likelihood is just a scalar whereas forward, backward
        # are matrices. Python is smart enough to replicate log_likelihood
        # to form a matrix of the right size. This is called broadcasting.
        state_posteriors = np.zeros([length, num_states])  # State posteriors.
        for pos in range(length):
            state_posteriors[pos, :] = forward[pos, :] + backward[pos, :]
            state_posteriors[pos, :] -= log_likelihood

        # Use the forward and backward variables along with the transition
        # and emission scores to obtain the transition posteriors.
        transition_posteriors = np.zeros([length-1, num_states, num_states])
        for pos in range(length-1):
            for prev_state in range(num_states):
                for state in range(num_states):
                    transition_posteriors[pos, state, prev_state] = \
                        forward[pos, prev_state] + \
                        transition_scores[pos, state, prev_state] + \
                        emission_scores[pos+1, state] + \
                        backward[pos+1, state]
                    transition_posteriors[pos, state, prev_state] -= log_likelihood

        state_posteriors = np.exp(state_posteriors)
        transition_posteriors = np.exp(transition_posteriors)

        return state_posteriors, transition_posteriors, log_likelihood

    def posterior_decode(self, sequence):
        """Compute the sequence of states that are individually the most
        probable, given the observations. This is done by maximizing
        the state posteriors, which are computed with the forward-backward
        algorithm."""

        # Compute scores given the observation sequence.
        initial_scores, transition_scores, final_scores, emission_scores = \
            self.compute_scores(sequence)

        state_posteriors, _, _ = self.compute_posteriors(initial_scores,
                                                         transition_scores,
                                                         final_scores,
                                                         emission_scores)
        best_states = np.argmax(state_posteriors, axis=1)
        predicted_sequence = sequence.copy_sequence()
        predicted_sequence.y = best_states
        return predicted_sequence

    def posterior_decode_corpus(self, dataset):
        """Run posterior_decode at corpus level."""
        predictions = []
        for sequence in dataset.seq_list:
            predictions.append(self.posterior_decode(sequence))
        return predictions

    def viterbi_decode(self, sequence):
        """Compute the most likely sequence of states given the observations,
        by running the Viterbi algorithm."""

        # Compute scores given the observation sequence.
        initial_scores, transition_scores, final_scores, emission_scores = \
            self.compute_scores(sequence)

        # Run the forward algorithm.
        best_states, total_score = self.decoder.run_viterbi(initial_scores,
                                                            transition_scores,
                                                            final_scores,
                                                            emission_scores)

        predicted_sequence = sequence.copy_sequence()
        predicted_sequence.y = best_states
        return predicted_sequence, total_score

    def viterbi_decode_corpus(self, dataset):
        """Run viterbi_decode at corpus level."""

        predictions = []
        for sequence in dataset.seq_list:
            predicted_sequence, _ = self.viterbi_decode(sequence)
            predictions.append(predicted_sequence)
        return predictions

    def evaluate_corpus(self, dataset, predictions):
        """Evaluate classification accuracy at corpus level, comparing with
        gold standard."""
        total = 0.0
        correct = 0.0
        for i, sequence in enumerate(dataset.seq_list):
            pred = predictions[i]
            for j, y_hat in enumerate(pred.y):
                if sequence.y[j] == y_hat:
                    correct += 1
                total += 1
        return correct / total
