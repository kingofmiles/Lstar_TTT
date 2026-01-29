# my_ttt/dfa.py
from graphviz import Digraph


class DFA:
    def __init__(self, states, start_state, accepting, transitions, state_repr=None):
        """
        states: set of states (internal typically tuple)
        start_state: start state (tuple)
        accepting: set of accepting states (tuple)
        transitions: dict[state][symbol] -> state
        state_repr: optional dict[state] -> string name (S0,S1,...)
        """
        self.states = set(states)
        self.start = start_state
        self.accepting = set(accepting)
        self.transitions = transitions

        # stable names: start is S0, rest sorted
        if state_repr is None:
            ordered = [self.start] + sorted([s for s in self.states if s != self.start], key=lambda x: str(x))
            self.state_repr = {s: f"S{i}" for i, s in enumerate(ordered)}
        else:
            self.state_repr = state_repr

    def __repr__(self):
        return f"DFA(start={self.start}, #states={len(self.states)}, #accepting={len(self.accepting)})"

    def accepts(self, seq):
        s = self.start
        for a in seq:
            s = self.transitions.get(s, {}).get(a)
            if s is None:
                return False
        return s in self.accepting

    def visualize(self, filename="dfa_ttt", title="Learned DFA (TTT)",
                  accept_label="accept: snapshot complete", reject_label="reject"):
        """
        Poster-friendly visualization:
        - Node names S0,S1,... with semantic labels
        - Accepting nodes doublecircle
        - Merge parallel edge labels
        Output: filename.pdf
        """

        dot = Digraph(comment=title)
        dot.attr(rankdir="TB")
        dot.attr("graph", fontsize="18")
        dot.attr("node", fontsize="16")
        dot.attr("edge", fontsize="14")

        # ensure all states have names
        for s in self.states:
            if s not in self.state_repr:
                self.state_repr[s] = f"S{len(self.state_repr)}"

        # nodes
        # order: start first then others (stable)
        ordered = [self.start] + sorted([s for s in self.states if s != self.start], key=lambda x: str(x))
        for s in ordered:
            s_name = self.state_repr[s]
            is_acc = s in self.accepting
            shape = "doublecircle" if is_acc else "circle"
            label = f"{s_name}\n({accept_label})" if is_acc else f"{s_name}\n({reject_label})"
            dot.node(s_name, label, shape=shape)

        # start arrow
        dot.node("__start__", "", shape="point")
        dot.edge("__start__", self.state_repr[self.start])

        # merge edges
        merged = {}  # (src_name,dst_name) -> set(symbols)
        for s, trans in self.transitions.items():
            s_name = self.state_repr[s]
            for a, t in trans.items():
                t_name = self.state_repr.get(t)
                if t_name is None:
                    t_name = f"S{len(self.state_repr)}"
                    self.state_repr[t] = t_name
                    dot.node(t_name, f"{t_name}\n({reject_label})", shape="circle")
                merged.setdefault((s_name, t_name), set()).add(str(a))

        for (s_name, t_name), syms in merged.items():
            dot.edge(s_name, t_name, label=",".join(sorted(syms)))

        dot.render(filename, format="pdf", cleanup=True)
