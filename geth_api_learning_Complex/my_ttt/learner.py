# my_ttt/learner.py
from my_ttt.dfa import DFA
from my_ttt.node import DTNode


class TTTLearner:
    def __init__(self, alphabet, membership_oracle, equivalence_oracle):
        self.A = list(alphabet)
        self.mq_raw = membership_oracle
        self.eq = equivalence_oracle

        self.root = DTNode([], is_leaf=False)
        self.states = {}

        # MQ cache: tuple(seq) -> bool
        self._mq_cache = {}

    # ---------- utilities ----------
    def _to_list(self, seq):
        if seq is None:
            return []
        if isinstance(seq, list):
            return seq
        if isinstance(seq, tuple):
            return list(seq)
        if isinstance(seq, str):
            return list(seq)
        return list(seq)

    def mq(self, seq):
        seq_list = self._to_list(seq)
        key = tuple(seq_list)
        if key in self._mq_cache:
            return self._mq_cache[key]
        ans = bool(self.mq_raw(seq_list))
        self._mq_cache[key] = ans
        return ans

    # ---------- discrimination tree ----------
    def sift(self, seq):
        seq = self._to_list(seq)
        node = self.root
        while not node.is_leaf():
            d = node.discriminator if node.discriminator is not None else []
            res = self.mq(seq + d)
            if res not in node.children:
                node.children[res] = DTNode([], is_leaf=True)
                node.children[res].rep = []
                self.states[node.children[res]] = []
            node = node.children[res]
        return node

    def _ensure_leaf_rep(self, leaf):
        if getattr(leaf, "rep", None) is None:
            leaf.rep = []
        return leaf.rep

    # ---------- main learning loop ----------
    def learn(self, max_rounds=300, max_refinements=80):
        # init leaves for True/False
        true_leaf = DTNode([], is_leaf=True)
        false_leaf = DTNode([], is_leaf=True)

        false_leaf.rep = []

        # try find a short True witness for true_leaf
        true_witness = None
        for a in self.A:
            if self.mq([a]) is True:
                true_witness = [a]
                break
        if true_witness is None:
            # fallback: leave empty; refinement will fix later
            true_witness = []

        true_leaf.rep = true_witness

        self.root.children = {True: true_leaf, False: false_leaf}
        self.states = {true_leaf: true_leaf.rep, false_leaf: false_leaf.rep}

        rounds = 0
        refinements = 0

        while True:
            rounds += 1
            if rounds > max_rounds:
                print(f"[TTT] stop: round limit {max_rounds}")
                return self.build_dfa()

            hypothesis = self.build_dfa()
            ce = self.eq(hypothesis)

            if ce is None:
                return hypothesis

            ce_list = self._to_list(ce)

            ok = self.refine(ce_list)
            if not ok:
                print("[TTT] refine failed (no separating split); returning best-effort DFA")
                return self.build_dfa()

            refinements += 1
            if refinements >= max_refinements:
                print(f"[TTT] stop: refinement limit {max_refinements}")
                return self.build_dfa()

    # ---------- refinement ----------
    def refine(self, ce):
        """
        refine:
        1) Frist, check 1-step discriminator [a]
        2) If that fails, try using the suffix ce[i:] of counterexample as the discriminator (which is stronger).
        """
        ce = self._to_list(ce)

        # Pass 1: your original 1-step split
        for i in range(len(ce) + 1):
            prefix = ce[:i]
            leaf = self.sift(prefix)
            rep = self._ensure_leaf_rep(leaf)

            for a in self.A:
                if self.mq(prefix + [a]) != self.mq(rep + [a]):
                    disc = [a]
                    return self._split_leaf(leaf, prefix, rep, disc)

        # Pass 2: suffix-based discriminator (key improvement)
        # Try to separate prefix and its leaf representative using a longer suffix.
        for i in range(len(ce) + 1):
            prefix = ce[:i]
            leaf = self.sift(prefix)
            rep = self._ensure_leaf_rep(leaf)

            # if prefix and rep already same rep, still may need split using suffix
            suffix = ce[i:]  # possibly empty

            # Skip empty suffix: no information
            if len(suffix) == 0:
                continue

            # Check if suffix distinguishes prefix vs rep
            if self.mq(prefix + suffix) != self.mq(rep + suffix):
                disc = suffix[:]  # use full suffix as discriminator
                return self._split_leaf(leaf, prefix, rep, disc)

        return False

    def _split_leaf(self, leaf, rep1, rep2, disc):
        rep1 = list(rep1)
        rep2 = list(rep2)
        disc = list(disc)

        b1 = self.mq(rep1 + disc)
        b2 = self.mq(rep2 + disc)

        if b1 == b2:
            return False

        new_node = DTNode(disc, is_leaf=False)

        child1 = DTNode(rep1, is_leaf=True)
        child1.rep = rep1
        child2 = DTNode(rep2, is_leaf=True)
        child2.rep = rep2

        new_node.children[b1] = child1
        new_node.children[b2] = child2

        leaf.become(new_node)

        if child1 not in self.states:
            self.states[child1] = child1.rep
        if child2 not in self.states:
            self.states[child2] = child2.rep

        return True

    # ---------- DFA construction ----------
    def build_dfa(self):
        accepting = set()
        transitions = {}
        all_states = set()

        # collect states from current leaves
        for leaf, rep in list(self.states.items()):
            rep = self._to_list(rep)
            leaf.rep = rep
            st = tuple(rep)
            all_states.add(st)
            if self.mq(rep):
                accepting.add(st)

        start = tuple([])
        all_states.add(start)

        # transitions
        for st in list(all_states):
            st_list = list(st)
            transitions[st] = {}
            for a in self.A:
                t_leaf = self.sift(st_list + [a])
                t_rep = self._ensure_leaf_rep(t_leaf)
                transitions[st][a] = tuple(t_rep)
                all_states.add(tuple(t_rep))

        # one more closure pass (bounded)
        for st in list(all_states):
            if st not in transitions:
                st_list = list(st)
                transitions[st] = {}
                for a in self.A:
                    t_leaf = self.sift(st_list + [a])
                    t_rep = self._ensure_leaf_rep(t_leaf)
                    transitions[st][a] = tuple(t_rep)

        return DFA(
            states=set(transitions.keys()),
            start_state=start,
            accepting=accepting,
            transitions=transitions
        )
