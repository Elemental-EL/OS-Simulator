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
    READ = "Read"
    WRITE = "Write"


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


class MemoryInstruction(Instruction):
    """Class for instructions of type "Read" and "Write"."""

    def __init__(self, instruction_type: InstructionType, address: int):
        super().__init__(instruction_type)
        self.address = address


class Memory:
    """Main class for handling memory pages."""

    def __init__(self, page_size: int, page_count: int):
        self.page_size = page_size
        self.pages = deque(maxlen=page_count)
        self.frames: dict[Page: int] = {}
        self.free_frames: list[int] = list(range(page_count))
        heapq.heapify(self.free_frames)


class Page:
    """Main class for page instances."""

    def __init__(self, page_number: int):
        self.page_number = page_number
        self.dirty = False


class Process:
    """Main class representing each process."""

    def __init__(self, pid: int):
        self.pid = pid
        self.instructions = deque()


def FCFS(process_list, mem: Memory):
    events = []  # (type, pid, start, end) or (type, pid, X, res, t)
    global_time = 0

    ready = deque(process_list)
    waiting = []  # min-heap of (wake_time, pid, process)

    while ready or waiting:
        if not ready:
            wake_time, _, waiting_process = heapq.heappop(waiting)
            # advance to when it wakes
            global_time = max(global_time, wake_time)
            ready.append(waiting_process)
            # wake others at same time
            while waiting and waiting[0][0] == wake_time:
                _, _, p2 = heapq.heappop(waiting)
                ready.append(p2)
            continue

        ready_process = ready.popleft()
        pid = ready_process.pid

        # run until hitting a sleep (block) or finish
        while ready_process.instructions:
            instr = ready_process.instructions.popleft()
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
                heapq.heappush(waiting, (end, pid, ready_process))
                break

            elif instr.instruction_type in (InstructionType.READ, InstructionType.WRITE):
                start = global_time
                # Calculate the location to look for
                page_num = instr.address // mem.page_size
                page = next((page for page in mem.pages if page.page_number == page_num), None)
                if page is not None:
                    # Hit
                    if instr.instruction_type == InstructionType.READ:
                        events.append(("RM", pid, mem.frames[page], start))
                    else:
                        events.append(("WM", pid, mem.frames[page], start))
                        page.dirty = True
                    global_time = start + 20

                else:
                    # Miss, load the target page into memory
                    page = Page(page_num)
                    if mem.free_frames:
                        frame_id = heapq.heappop(mem.free_frames)
                    else:
                        evicted_page = mem.pages.popleft()
                        frame_id = mem.frames.pop(evicted_page)
                        # Write back the evicted page if dirty
                        if evicted_page.dirty:
                            events.append(("MTD", pid, evicted_page.page_number, frame_id, start))
                            start += 40
                    mem.frames[page] = frame_id
                    mem.pages.append(page)
                    events.append(("DTM", pid, page_num, frame_id, start))
                    if instr.instruction_type == InstructionType.READ:
                        events.append(("RM", pid, frame_id, start + 40))
                    else:
                        events.append(("WM", pid, frame_id, start + 40))
                        page.dirty = True
                    global_time = start + 60
                # continue to next instruction

            else:
                # skip resource instructions under FCFS (For now)
                continue
        # if loop exited naturally (no sleep) => done
    return events


n_processes: int = int(input())  # Number of processes
m_resources: int = int(input())  # Number of resource types
resource_instances = list(map(int, input().split()))  # Number of each resource type
ps, pc = input().split()  # Page size and Page frames

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
        elif InstructionType(instruction[0]) in (InstructionType.READ, InstructionType.WRITE):
            # Enqueue The instruction for the process
            process.instructions.append(MemoryInstruction(InstructionType(instruction[0]), int(instruction[1])))
        else:
            # Invalid instruction handling
            ValueError("Invalid instruction type")
    processes.append(process)

# Create memory
memory = Memory(int(ps), int(pc))

res = FCFS(processes, memory)
print(len(res))
for event in res:
    print(" ".join(str(x) for x in event))
