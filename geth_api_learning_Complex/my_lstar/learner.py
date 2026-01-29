from .observation_table import ObservationTable
from graphviz import Digraph

# my_lstar/dfa.py
from graphviz import Digraph


class DFA:
    """
    DFA object with accepts() used by equivalence oracle.
    states: iterable of hashable states (e.g., tuples)
    transitions: dict[state][symbol] -> state
    start_state: state
    accepting: set of accepting states
    """

    def __init__(self, states, transitions, start_state, accepting):
        self.states = set(states)
        self.transitions = transitions
        self.start_state = start_state
        self.accepting = set(accepting)

    def accepts(self, sequence):
        current_state = self.start_state
        for symbol in sequence:
            current_state = self.transitions.get(current_state, {}).get(symbol)
            if current_state is None:
                return False
        return current_state in self.accepting

    def __repr__(self):
        return f"DFA(start={self.start_state}, #states={len(self.states)}, #accepting={len(self.accepting)})"

    def visualize(self, filename="dfa_lstar", title="Learned DFA (L*)",
                  accept_label="accept: snapshot complete", reject_label="reject"):
        """
        Poster-friendly visualization:
        - Map raw tuple states -> S0,S1,...
        - Node label shows accept/reject semantics
        - Merge parallel edges labels
        Output: filename.pdf
        """

        dot = Digraph(comment=title)
        dot.attr(rankdir="TB")  # top-to-bottom
        dot.attr("graph", fontsize="18")
        dot.attr("node", fontsize="16")
        dot.attr("edge", fontsize="14")

        # ---------- stable state ordering: start first, then others ----------
        others = [s for s in self.states if s != self.start_state]
        others = sorted(others, key=lambda x: str(x))
        ordered_states = [self.start_state] + others

        state_id = {s: f"S{i}" for i, s in enumerate(ordered_states)}

        # ---------- nodes ----------
        for s in ordered_states:
            sid = state_id[s]
            is_acc = s in self.accepting
            shape = "doublecircle" if is_acc else "circle"
            label = f"{sid}\n({accept_label})" if is_acc else f"{sid}\n({reject_label})"
            dot.node(sid, label=label, shape=shape)

        # start arrow
        dot.node("__start__", "", shape="point")
        dot.edge("__start__", state_id[self.start_state])

        # ---------- merge parallel edges: (src,dst)->set(symbols) ----------
        merged = {}  # (src_id, dst_id) -> set(symbols)
        for s, trans in self.transitions.items():
            if s not in state_id:
                continue
            s_id = state_id[s]
            for sym, t in trans.items():
                if t not in state_id:
                    # if a transition points to unknown state, still show it (rare)
                    # create a placeholder name
                    state_id[t] = f"S{len(state_id)}"
                    dot.node(state_id[t], label=f"{state_id[t]}\n({reject_label})", shape="circle")
                t_id = state_id[t]
                merged.setdefault((s_id, t_id), set()).add(str(sym))

        for (s_id, t_id), syms in merged.items():
            label = ",".join(sorted(syms))
            dot.edge(s_id, t_id, label=label)

        dot.render(filename, format="pdf", cleanup=True)



class LStar:
    def __init__(self, alphabet, membership_oracle, equivalence_oracle):
        self.alphabet = list(alphabet)
        self.mq = membership_oracle
        self.eq = equivalence_oracle
        self.table = ObservationTable(self.alphabet)

    def learn(self):
        # Initialization
        self.table.init_table(self.mq)

        while True:
            while True:
                is_closed, p = self.table.closed()
                is_consistent, _, s = self.table.consistent()

                if is_closed and is_consistent:
                    break
                if not is_closed:
                    self.table.add_prefix(p, self.mq)
                if not is_consistent:
                    self.table.add_suffix(s, self.mq)

            # Generate DFA
            hypothesis_dict = self.table.to_dfa()

            hypothesis = DFA(
                states=hypothesis_dict["states"],
                transitions=hypothesis_dict["transitions"],
                start_state=hypothesis_dict["start_state"],
                accepting=hypothesis_dict["accepting"]
            )

            # Get counterexample
            counterexample = self.eq(hypothesis)

            if counterexample is None:
                # all good, Finish
                return hypothesis

            # Find counterexample
            self.table.add_counterexample(counterexample, self.mq)

