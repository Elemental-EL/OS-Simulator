import heapq
from abc import ABC
from collections import deque
from enum import Enum


class InstructionType(Enum):
    """Enum class for each type of instruction that is used here."""
    RUN = "Run"
    SLEEP = "Sleep"
    ALLOCATE = "Allocate"
    FREE = "Free"


class Instruction(ABC):
    """Abstract base class for all instructions."""

    def __init__(self, instruction_type: InstructionType):
        self.instruction_type = instruction_type


class CpuInstruction(Instruction):
    """Class for instructions of type "Run" and "Sleep"."""

    def __init__(self, instruction_type: InstructionType, duration: int):
        super().__init__(instruction_type)
        self.duration = duration


class ResourceInstruction(Instruction):
    """Class for instructions of type "Allocate" and "Free"."""

    def __init__(self, instruction_type: InstructionType, number_of_instances: int, instance_id: int):
        super().__init__(instruction_type)
        self.number_of_instances = number_of_instances
        self.instance_id = instance_id


class Process:
    """Main class representing each process."""

    def __init__(self, pid: int):
        self.pid = pid
        self.instructions = deque()


def FCFS(process_list):
    events = []  # (type, pid, start, end) or (type, pid, X, res, t)
    global_time = 0

    ready = deque(process_list)
    waiting = []  # min-heap of (wake_time, pid, process)

    while ready or waiting:
        if not ready:
            wake_time, _, process = heapq.heappop(waiting)
            # advance to when it wakes
            global_time = max(global_time, wake_time)
            ready.append(process)
            # wake others at same time
            while waiting and waiting[0][0] == wake_time:
                _, _, p2 = heapq.heappop(waiting)
                ready.append(p2)
            continue

        process = ready.popleft()
        pid = process.pid

        # run until hitting a sleep (block) or finish
        while process.instructions:
            instr = process.instructions.popleft()
            if instr.instruction_type == InstructionType.RUN:
                start = global_time
                end = start + instr.duration
                events.append(("EXECUTE", pid, start, end))
                global_time = end
                # continue to next instruction

            elif instr.instruction_type == InstructionType.SLEEP:
                # block: record wait, schedule wake, then stop
                start = global_time
                end = start + instr.duration
                events.append(("WAIT", pid, start, end))
                heapq.heappush(waiting, (end, pid, process))
                break

            else:
                # skip resource instructions under FCFS (For now)
                continue
        # if loop exited naturally (no sleep) => done
    return events


n_processes: int = int(input())  # Number of processes
m_resources: int = int(input())  # Number of resource types
resource_instances = list(map(int, input().split()))  # Number of each resource type
ps, pc = input().split()  # Page size and Page frames (Will read zero)

# Create process instances
processes = []
for i in range(n_processes):
    process = Process(pid=i)
    instruction_count = int(input())
    # Read each line of instruction related to the process
    for j in range(instruction_count):
        instruction = input().split()
        # Distinguish the type of instruction
        if InstructionType(instruction[0]) in (InstructionType.RUN, InstructionType.SLEEP):
            # Enqueue The instruction for the process
            process.instructions.append(CpuInstruction(InstructionType(instruction[0]), int(instruction[1])))
        elif InstructionType(instruction[0]) in (InstructionType.ALLOCATE, InstructionType.FREE):
            # Enqueue The instruction for the process
            process.instructions.append(
                ResourceInstruction(InstructionType(instruction[0]), int(instruction[1]), int(instruction[2])))
        else:
            # Invalid instruction handling
            ValueError("Invalid instruction type")
    processes.append(process)

res = FCFS(processes)
print(len(res))
for typ, pid, s, e in res:
    print(f"{typ} {pid} {s} {e}")

# TODO: Implement deadlock prevention. (might add memory management as well)
