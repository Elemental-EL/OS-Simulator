from abc import ABC
from enum import Enum
from queue import Queue


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
        self.instructions = Queue()


n_processes: int = int(input())  # Number of processes
m_resources: int = int(input())  # Number of resource types
resource_instances = list(map(int, input().split()))  # Number of each resource type
ps, pc = input().split()  # Page size and Page frames (Will read zero)

# Create process instances
for i in range(n_processes):
    process = Process(pid=i)
    instruction_count = int(input())
    # Read each line of instruction related to the process
    for j in range(instruction_count):
        instruction = input().split()
        # Distinguish the type of instruction
        if InstructionType(instruction[0]) == InstructionType.RUN or InstructionType(
                instruction[0]) == InstructionType.SLEEP:
            # Enqueue The instruction for the process
            process.instructions.put(CpuInstruction(InstructionType(instruction[0]), int(instruction[1])))
        elif InstructionType(instruction[0]) == InstructionType.ALLOCATE or InstructionType(
                instruction[0]) == InstructionType.FREE:
            # Enqueue The instruction for the process
            process.instructions.put(
                ResourceInstruction(InstructionType(instruction[0]), int(instruction[1]), int(instruction[2])))
        else:
            # Invalid instruction handling
            ValueError("Invalid instruction type")

# TODO: Implement scheduling policy
