class ObservationTable:
    def __init__(self, alphabet):
        self.A = list(alphabet)  # alphabet
        self.P = ['']            # prefixes
        self.S = ['']            # suffixes
        self._T = {}             # table[p][s] -> {0,1}

    # ---------- basic access ----------
    def cell(self, p, s):
        return self._T[p][s]

    def state(self, p):
        """返回一行的 tuple，用作 DFA 状态标识"""
        return tuple(self.cell(p, s) for s in self.S)

    # ---------- initialization ----------
    def init_table(self, oracle):
        self._T[''] = {'': oracle('')}
        self.update_table(oracle)

    def update_table(self, oracle):
        def uniq(xs):
            return list(dict.fromkeys(xs))

        rows = self.P
        aux = [p + a for p in self.P for a in self.A]
        all_rows = uniq(rows + aux)

        for p in all_rows:
            if p not in self._T:
                self._T[p] = {}
            for s in self.S:
                if s not in self._T[p]:
                    self._T[p][s] = oracle(p + s)

    # ---------- closedness ----------
    def closed(self):
        states_in_P = {self.state(p) for p in self.P}
        for p in self.P:
            for a in self.A:
                pa = p + a
                if self.state(pa) not in states_in_P:
                    return False, pa
        return True, None

    def add_prefix(self, p, oracle):
        if p in self.P:
            return
        self.P.append(p)
        self.update_table(oracle)

    # ---------- consistency ----------
    def consistent(self):
        for p1 in self.P:
            for p2 in self.P:
                if p1 == p2:
                    continue
                if self.state(p1) == self.state(p2):
                    for a in self.A:
                        for s in self.S:
                            if self.cell(p1 + a, s) != self.cell(p2 + a, s):
                                return False, (p1, p2), a + s
        return True, None, None

    def add_suffix(self, s, oracle):
        if s in self.S:
            return
        self.S.append(s)
        self.update_table(oracle)

    # ---------- hypothesis construction ----------
    def to_dfa(self):
        """
        返回标准 DFA dict:
        {
            "states": [...],
            "start_state": ...,
            "accepting": [...],
            "transitions": {state: {symbol: next_state}}
        }
        """
        # 每个 row 的状态用 tuple 表示
        states_map = {}  # tuple(row) -> p 代表状态名字
        for p in self.P:
            st = self.state(p)
            if st not in states_map:
                states_map[st] = p  # 用前缀 p 作为状态标识

        states = list(states_map.keys())
        start_state = self.state('')

        # 接受状态
        accepting = [st for st, p in states_map.items() if self.cell(p, '') == 1]

        # transitions
        transitions = {}
        for st, p in states_map.items():
            transitions[st] = {}
            for a in self.A:
                next_state = self.state(p + a)
                transitions[st][a] = next_state

        return {
            "states": states,
            "start_state": start_state,
            "accepting": accepting,
            "transitions": transitions
        }

    # ---------- counterexample handling ----------
    def add_counterexample(self, ce, oracle):
        for i in range(1, len(ce) + 1):
            self.add_prefix(ce[:i], oracle)
