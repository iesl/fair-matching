import numpy as np
import time
import uuid

from models.Basic import Basic
from gurobipy import *


class FairIR(Basic):
    """Fair paper matcher via iterative relaxation.

    """

    def __init__(self, loads, loads_lb, coverages, weights, makespan=0):
        """Initialize.

        Args:
            loads - a list of integers specifying the maximum number of papers
                  for each reviewer.
            loads_lb - a list of ints specifying the minimum number of papers
                  for each reviewer.
            coverages - a list of integers specifying the number of reviews per
                 paper.
            weights - the affinity matrix (np.array) of papers to reviewers.
                   Rows correspond to reviewers and columns correspond to
                   papers.
            makespan - optional initial makespan value.

            Returns:
                initialized makespan matcher.
        """
        self.n_rev = np.size(weights, axis=0)
        self.n_pap = np.size(weights, axis=1)
        self.loads = loads
        self.loads_lb = loads_lb
        self.coverages = coverages
        self.weights = weights
        self.id = uuid.uuid4()
        self.m = Model("%s : FairIR" % str(self.id))
        self.makespan = makespan or 0.0
        self.solution = None

        self.m.setParam('OutputFlag', 0)

        self.load_ub_name = 'lib'
        self.load_lb_name = 'llb'
        self.cov_name = 'cov'
        self.ms_constr_prefix = 'ms'
        self.round_constr_prefix = 'round'

        # primal variables
        start = time.time()
        self.lp_vars = []
        for i in range(self.n_rev):
            self.lp_vars.append([])
            for j in range(self.n_pap):
                self.lp_vars[i].append(self.m.addVar(ub=1.0,
                                                     name=self.var_name(i, j)))
        self.m.update()
        print('Time to add vars %s' % (time.time() - start))

        start = time.time()
        # set the objective
        obj = LinExpr()
        for i in range(self.n_rev):
            for j in range(self.n_pap):
                obj += self.weights[i][j] * self.lp_vars[i][j]
        self.m.setObjective(obj, GRB.MAXIMIZE)
        print('Time to set obj %s' % (time.time() - start))

        start = time.time()
        # load upper bound constraints.
        for r, load in enumerate(self.loads):
            self.m.addConstr(sum(self.lp_vars[r]) <= load,
                             self.lub_constr_name(r))

        # load load bound constraints.
        if self.loads_lb is not None:
            for r, load in enumerate(self.loads_lb):
                self.m.addConstr(sum(self.lp_vars[r]) >= load,
                                 self.llb_constr_name(r))

        # coverage constraints.
        for p, cov in enumerate(self.coverages):
            self.m.addConstr(sum([self.lp_vars[i][p]
                                  for i in range(self.n_rev)]) == cov,
                             self.cov_constr_name(p))

        # makespan constraints.
        for p in range(self.n_pap):
            self.m.addConstr(sum([self.lp_vars[i][p] * self.weights[i][p]
                                  for i in range(self.n_rev)]) >= self.makespan,
                             self.ms_constr_name(p))
        self.m.update()
        print('Time to add constr %s' % (time.time() - start))

    def ms_constr_name(self, p):
        """Name of the makespan constraint for paper p."""
        return '%s%s' % (self.ms_constr_prefix, p)

    def lub_constr_name(self, r):
        """Name of load upper bound constraint for reviewer r."""
        return '%s%s' % (self.load_ub_name, r)

    def llb_constr_name(self, r):
        """Name of load lower bound constraint for reviewer r."""
        return '%s%s' % (self.load_lb_name, r)

    def cov_constr_name(self, p):
        """Name of coverage constraint for paper p."""
        return '%s%s' % (self.cov_name, p)

    def change_makespan(self, new_makespan):
        """Change the current makespan to a new_makespan value.

        Args:
            new_makespan - the new makespan constraint.

        Returns:
            Nothing.
        """
        for c in self.m.getConstrs():
            if c.getAttr("ConstrName").startswith(self.ms_constr_prefix):
                self.m.remove(c)
                # self.m.update()

        for p in range(self.n_pap):
            self.m.addConstr(sum([self.lp_vars[i][p] * self.weights[i][p]
                                  for i in range(self.n_rev)]) >= new_makespan,
                             self.ms_constr_prefix + str(p))
        self.makespan = new_makespan
        self.m.update()

    def sol_as_mat(self):
        if self.m.status == GRB.OPTIMAL or self.m.status == GRB.SUBOPTIMAL:
            solution = np.zeros((self.n_rev, self.n_pap))
            for v in self.m.getVars():
                i, j = self.indices_of_var(v)
                solution[i, j] = v.x
            self.solution = solution
            return solution
        else:
            raise Exception(
                'You must have solved the model optimally or suboptimally '
                'before calling this function.')

    def integral_sol_found(self):
        """Return true if all lp variables are integral."""
        sol = self.sol_as_dict()
        return all(sol[self.var_name(i, j)] == 1.0 or
                   sol[self.var_name(i, j)] == 0.0
                   for i in range(self.n_rev) for j in range(self.n_pap))

    def fix_assignment(self, i, j, val, log_file=None):
        """Round the variable x_ij to val."""
        if log_file:
            logging.info("\tROUNDING (REVIEWER, PAPER) %s TO VAL: %s" % (
                 str((i, j)), str(val)))
        self.lp_vars[i][j].ub = val
        self.lp_vars[i][j].lb = val

    def find_ms(self):
        """Find an the highest possible makespan.

        Perform a binary search on the makespan value. Each time, solve the
        makespan LP without the integrality constraint. If we can find a
        fractional value to one of these LPs, then we can round it.

        Args:
            None

        Return:
            Highest feasible makespan value found.
        """
        mn = 0.0
        mx = np.max(self.weights) * np.max(self.coverages)
        ms = mx
        # ms = 24.974999999999998  # mx
        # ms = 0.7
        best = None
        self.change_makespan(ms)
        # self.change_makespan(16.65)
        start = time.time()
        self.m.optimize()
        print('Time to solve %s' % (time.time() - start))
        for i in range(5):
            print('ITERATION %s ms %s' % (i, ms))
            if self.m.status == GRB.INFEASIBLE:
                mx = ms
                ms -= (ms - mn) / 2.0
            else:
                print(ms, self.objective_val())
                print(self.sol_as_mat())
                assert(best is None or ms > best)
                assert(self.m.status == GRB.OPTIMAL)
                best = ms
                mn = ms
                ms += (mx - ms) / 2.0
            print('starting change_makespan')
            start = time.time()
            self.change_makespan(ms)
            print('Time to change makespan %s' % (time.time() - start))
            print('starting optimize')
            start = time.time()
            self.m.optimize()
            print('Time to solve %s' % (time.time() - start))
            print('ending optimize')
        print('Best found %s' % best)
        return best

    # find an appropriate makespan using binary search and solve
    def solve(self, mn=0, mx=-1, itr=10, log_file=None):
        """Find a makespan and solve the ILP.

        Run a binary search to find an appropriate makespan and then solve the
        ILP. If solved optimally or suboptimally then save the solution.

        Args:
            mn - the minimum feasible makespan (optional).
            mx - the maximum possible makespan( optional).
            itr - the number of iterations of binary search for the makespan.
            log_file - the string path to the log file.

        Returns:
            The solution as a matrix.
        """
        # TODO(AK)): Does this even do anything?
        # for c in self.m.getConstrs():
        #     if c.ConstrName.startswith(self.round_constr_prefix):
        #         print("SURPRISE! REMOVING A CONSTRAINT: %s" % str(c))
        #         self.m.remove(c)
        #         assert(False)

        ms = self.find_ms()
        # ms = 16.65
        # ms = 24.974999999999998
        # ms = 18.73125
        # ms = 22.22
        # ms = 16.52
        self.change_makespan(ms)

        begin_opt = time.time()
        self.round_fractional(np.ones((self.n_rev, self.n_pap)) * -1, log_file)
        end_opt = time.time()
        if log_file:
            logging.info('#solver-time\t%s' % (str(end_opt - begin_opt)))

        sol = {}
        for v in self.m.getVars():
            sol[v.varName] = v.x

        if log_file:
            logging.info('#obj\t%f' % self.objective_val())

    def round_fractional(self, integral_assignments=None, log_file=None,
                         count=0):
        """Round a fractional solution.

        This is the meat of the iterative relaxation approach.  First, if the
        solution to the relaxed LP is integral, then we're done--return the
        solution. Otherwise, here's what we do:
        1. if a variable is integral, lock it's value to that integer.
        2. find one paper with exactly 2 fractionally assigned reviewers and
           drop the makespan constraint on that reviewer.

        Args:
            integral_assignments - np.array of revs x paps (initially None).
            log_file - the log file if exists.
            count - (int) to keep track of the number of calls to this function.

        Returns:
            Nothing--has the side effect or storing an assignment matrix in this
            class.
        """
        if integral_assignments is None:
            integral_assignments = np.ones((self.n_rev, self.n_pap)) * -1

        self.m.optimize()

        print("FINSHED OPTIMIZTION")

        if self.m.status != GRB.OPTIMAL and self.m.status != GRB.SUBOPTIMAL:
            assert False, '%s\t%s' % (self.m.status, self.makespan)

        if self.integral_sol_found():
            if log_file:
                logging.info('[#ITERATIONS]: %d' % count)
            return
        else:
            if log_file:
                logging.info('[BEGIN ROUNDING ITERATION]: %d' % count)
            frac_assign_p = {}
            frac_assign_r = {}
            sol = self.sol_as_dict()
            fractional_vars = []

            # Find fractional vars.
            for i in range(self.n_rev):
                for j in range(self.n_pap):
                    if j not in frac_assign_p:
                        frac_assign_p[j] = []
                    if i not in frac_assign_r:
                        frac_assign_r[i] = []

                    if sol[self.var_name(i, j)] == 0.0 and \
                                    integral_assignments[i][j] != 0.0:
                        self.fix_assignment(i, j, 0.0, log_file)
                        integral_assignments[i][j] = 0.0

                    elif sol[self.var_name(i, j)] == 1.0 and \
                                    integral_assignments[i][j] != 1.0:
                        self.fix_assignment(i, j, 1.0, log_file)
                        integral_assignments[i][j] = 1.0

                    elif sol[self.var_name(i, j)] != 1.0 and \
                                    sol[self.var_name(i, j)] != 0.0:
                        frac_assign_p[j].append(
                            (i, j, sol[self.var_name(i, j)]))
                        frac_assign_r[i].append(
                            (i, j, sol[self.var_name(i, j)]))
                        fractional_vars.append((i, j, sol[self.var_name(i, j)]))

                        integral_assignments[i][j] = sol[self.var_name(i, j)]

            # First try to elim a makespan constraint.
            removed = False
            for (paper, frac_vars) in frac_assign_p.items():
                if len(frac_vars) == 2 or len(frac_vars) == 3:
                    for c in self.m.getConstrs():
                        if c.ConstrName == self.ms_constr_name(paper):
                            self.m.remove(c)
                            removed = True

            # If necessary remove a load constraint.
            if not removed:
                for (rev, frac_vars) in frac_assign_r.items():
                    if len(frac_vars) == 2:
                        for c in self.m.getConstrs():
                            if c.ConstrName == self.lub_constr_name(rev) or \
                                    c.ConstrName == self.llb_constr_name(rev):
                                self.m.remove(c)
            self.m.update()
            return self.round_fractional(integral_assignments, log_file,
                                         count + 1)


if __name__ == "__main__":
    init_makespan = 0.7
    ws = np.array([
        np.array([0.9, 0.9, 0.5, 0.5]),
        np.array([0.9, 0.9, 0.6, 0.6]),
        np.array([0.1, 0.1, 0.2, 0.2]),
        np.array([0.2, 0.1, 0.2, 0.3])
    ])
    print(ws)
    a = np.array([2, 2, 2, 2])
    b = np.array([2, 2, 2, 2])
    x = FairIR(a, [0, 0, 0, 0], b, ws)
    s = time.time()
    x.solve()
    print(x.sol_as_mat())
    print(x.objective_val())
    print(time.time() - s)
    print("[done.]")
