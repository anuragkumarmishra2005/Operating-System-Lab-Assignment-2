"""
================================================================
  Deadlock Avoidance using Banker's Algorithm
  Course  : Operating System Lab (ENCA252)
  Program : BCA (AI & DS)
  Name    : Anurag Kumar Mishra
  Roll No : 2401201076
================================================================
"""

import os

# ================================================================
# SECTION 1 — System Input & Data Collection
# ================================================================

def read_system_data():
    """
    Collect all required system information from the user.
    Returns a dictionary containing all matrices and vectors.
    """

    print("#" * 58)
    print("#     DEADLOCK AVOIDANCE — BANKER'S ALGORITHM           #")
    print("#" * 58)

    # Total number of processes and distinct resource categories
    num_proc = int(input("\nTotal number of processes        : "))
    num_res  = int(input("Total number of resource types   : "))

    # ── Currently Held Resources (Allocation Table) ────────────
    print(f"\n[Allocation Table] — {num_proc} processes x {num_res} resource types")
    print("Enter each row as space-separated integers:")
    alloc_table = []
    for i in range(num_proc):
        row = list(map(int, input(f"  Process {i} : ").split()))
        alloc_table.append(row)

    # ── Peak Demand Matrix (Max Table) ─────────────────────────
    print(f"\n[Peak Demand Table] — {num_proc} processes x {num_res} resource types")
    print("Enter each row as space-separated integers:")
    peak_table = []
    for i in range(num_proc):
        row = list(map(int, input(f"  Process {i} : ").split()))
        peak_table.append(row)

    # ── Free Resources Vector ──────────────────────────────────
    print(f"\n[Free Resources] — enter {num_res} space-separated values:")
    free_res = list(map(int, input("  Free : ").split()))

    return {
        "num_proc"   : num_proc,
        "num_res"    : num_res,
        "alloc_table": alloc_table,
        "peak_table" : peak_table,
        "free_res"   : free_res,
    }


def show_matrix(label, matrix, num_proc, num_res):
    """Display any 2D matrix in a readable tabular format."""
    print(f"\n{'~' * 42}")
    print(f"  {label}")
    print(f"{'~' * 42}")
    col_header = "        " + "   ".join([f"R{j}" for j in range(num_res)])
    print(col_header)
    for i in range(num_proc):
        vals = "   ".join(str(v).rjust(2) for v in matrix[i])
        print(f"  Proc{i}  [ {vals} ]")


def show_vector(label, vec):
    """Display a 1-D resource vector."""
    print(f"\n  {label} : {vec}")


# ================================================================
# SECTION 2 — Remaining Need Matrix Calculation
# ================================================================

def compute_remaining(peak_table, alloc_table, num_proc, num_res):
    """
    Build the Remaining Need matrix.

    Formula:
        Remaining[i][j] = PeakDemand[i][j] - CurrentAlloc[i][j]

    This tells us how many more resources each process
    might still request before it finishes.
    """
    remaining = []
    for i in range(num_proc):
        row = [peak_table[i][j] - alloc_table[i][j] for j in range(num_res)]
        remaining.append(row)
    return remaining


# ================================================================
# SECTION 3 — Safety Check Algorithm
# SECTION 4 — Safe Execution Sequence
# ================================================================

def check_safety(num_proc, num_res, alloc_table, remaining, free_res):
    """
    Banker's Safety Check — determines if the system is in a safe state.

    How it works:
    -------------
    1. Set buffer = copy of free_res  (we simulate without touching real data)
    2. Mark every process as incomplete (done[i] = False)
    3. Scan for a process whose remaining need fits within buffer
    4. Simulate that process completing: add its allocation back to buffer
    5. Mark it done and record it in the execution order
    6. Keep scanning until all are done (SAFE) or none can proceed (UNSAFE)

    Returns:
        safe    : bool  — True if a safe sequence was found
        order   : list  — The safe execution sequence (process indices)
    """

    buffer = free_res[:]           # Working copy — simulates available pool
    done   = [False] * num_proc    # Tracks which processes have completed
    order  = []                    # Records the safe execution order
    step   = 0

    print("\n" + "#" * 58)
    print("#        SAFETY CHECK — DETAILED TRACE                 #")
    print("#" * 58)
    print(f"  Starting Buffer (Free Resources) : {buffer}\n")

    while len(order) < num_proc:
        progress = False

        for i in range(num_proc):
            if done[i]:
                continue   # already scheduled, skip

            # Check: can this process's remaining need be satisfied?
            can_run = all(remaining[i][j] <= buffer[j] for j in range(num_res))

            if can_run:
                # Simulate process completing and releasing its resources
                prev_buffer = buffer[:]
                buffer = [buffer[j] + alloc_table[i][j] for j in range(num_res)]
                done[i]  = True
                order.append(i)
                progress = True
                step += 1

                print(f"  Step {step}: Process {i} scheduled")
                print(f"    Remaining Need : {remaining[i]}")
                print(f"    Buffer Before  : {prev_buffer}")
                print(f"    Buffer After   : {buffer}")
                print()
                break   # restart scan from Process 0

        if not progress:
            # No process could be scheduled — system may deadlock
            break

    is_safe = all(done)
    return is_safe, order


# ================================================================
# SECTION 5 — Output, Analysis & Verdict
# ================================================================

def show_verdict(is_safe, order, num_proc):
    """
    Print the final result of the safety check along with
    a clear explanation of what the outcome means.
    """

    print("#" * 58)
    print("#                FINAL VERDICT                         #")
    print("#" * 58)

    if is_safe:
        seq = " --> ".join([f"P{p}" for p in order])
        print("\n  [SAFE]  System is currently in a SAFE STATE.")
        print(f"\n  Execution Order : {seq}")
        print("""
  What this means:
  ~~~~~~~~~~~~~~~~
  A valid execution sequence was found in which every
  process can eventually acquire all the resources it
  needs, run to completion, and then return those
  resources to the pool. Since such a sequence exists,
  the system is guaranteed to be free from deadlock
  under the current resource allocation.
        """)
    else:
        scheduled   = set(order)
        blocked     = [f"P{i}" for i in range(num_proc) if i not in scheduled]
        partial_seq = " --> ".join([f"P{p}" for p in order]) if order else "None"

        print("\n  [UNSAFE]  System is in an UNSAFE STATE.")
        print(f"\n  Partial Sequence         : {partial_seq}")
        print(f"  Processes that are stuck : {blocked}")
        print("""
  What this means:
  ~~~~~~~~~~~~~~~~
  The algorithm could not find a complete safe sequence.
  The blocked processes listed above cannot proceed
  because each one needs more resources than the system
  can currently provide, even after simulating all
  possible orderings. The system is therefore at risk
  of deadlock if these processes continue to hold
  their currently allocated resources.
        """)


# ================================================================
# MAIN — Entry point, ties all sections together
# ================================================================

def main():
    os.system("clear" if os.name == "posix" else "cls")

    # ── Section 1: Collect Input ──────────────────────────────
    data       = read_system_data()
    num_proc   = data["num_proc"]
    num_res    = data["num_res"]
    alloc_table = data["alloc_table"]
    peak_table  = data["peak_table"]
    free_res    = data["free_res"]

    # Print summary of what was entered
    print("\n" + "#" * 58)
    print("#               INPUT SUMMARY                          #")
    print("#" * 58)
    show_matrix("Allocation Table",  alloc_table, num_proc, num_res)
    show_matrix("Peak Demand Table", peak_table,  num_proc, num_res)
    show_vector("Free Resources",    free_res)

    # ── Section 2: Compute Remaining Need ─────────────────────
    remaining = compute_remaining(peak_table, alloc_table, num_proc, num_res)
    show_matrix("Remaining Need  (Peak - Allocated)", remaining, num_proc, num_res)

    # ── Section 3 & 4: Run Safety Algorithm ───────────────────
    is_safe, order = check_safety(num_proc, num_res, alloc_table, remaining, free_res)

    # ── Section 5: Show Final Verdict ─────────────────────────
    show_verdict(is_safe, order, num_proc)


# ── Run only when executed directly ──────────────────────────
if __name__ == "__main__":
    main()
