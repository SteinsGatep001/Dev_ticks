# coding: utf-8
import re

from qhost.hostgdb.qavatar2 import QCustomAvatar
from qhost.hostgdb.qgdb_target import CustomGDBTarget
from .memory_map import CustomMemoryMap
from avatar2 import *
from angr.errors import SimConcreteMemoryError, SimConcreteRegisterError, SimConcreteBreakpointError

from angr_targets.concrete import ConcreteTarget
from angr_targets.target_states import TargetStates


class ArmVMGDBConcreteTarget(ConcreteTarget):
    """
    Concrete target to operate gdb
    """

    def __init__(self, architecture, gdbserver_ip, gdbserver_port):
        """
        concrete target modified from avatar2
        :param architecture:
        :param gdbserver_ip:
        :param gdbserver_port:
        """
        # Creation of the avatar-object
        # self.avatar = Avatar(arch=architecture)
        self.avatar = QCustomAvatar(arch=architecture)
        self.architecture = architecture
        self.target = self.avatar.add_target(CustomGDBTarget, gdb_executable="gdb-multiarch", gdb_ip=gdbserver_ip,
                                             gdb_port=gdbserver_port)
        self.avatar.init_targets()
        self.page_size = 0x1000  # I want this to be passed by the project in a clean way..
        super(ArmVMGDBConcreteTarget, self).__init__()

    def exit(self):
        self.avatar.shutdown()

    def read_memory(self, address, nbytes, **kwargs):
        try:
            arm_target_log.debug("ArmVMGDBConcreteTarget read_memory at %x " % (address))
            page_end = (address | (self.page_size - 1)) + 1

            if address + nbytes > page_end:
                nbytes = page_end - address

            res = self.target.read_memory(address, 1, int(nbytes), raw=True)
            return res
        except Exception as e:
            arm_target_log.debug("ArmVMGDBConcreteTarget can't read_memory at address %x exception %s" % (address, e))
            raise SimConcreteMemoryError(
                "ArmVMGDBConcreteTarget can't read_memory at address %x exception %s" % (address, e))

    def write_memory(self, address, value, **kwargs):
        # arm_target_log.debug("ArmVMGDBConcreteTarget write_memory at %x value %s " %(address, value.encode("hex")))
        try:
            res = self.target.write_memory(address, 1, value, raw=True)
            if not res:
                arm_target_log.warning("ArmVMGDBConcreteTarget failed write_memory at %x value %s" % (address, value))
                raise SimConcreteMemoryError("ArmVMGDBConcreteTarget failed write_memory to address %x" % (address))
        except Exception as e:
            arm_target_log.warning(
                "ArmVMGDBConcreteTarget write_memory at %x value %s exception %s" % (address, value, e))
            raise SimConcreteMemoryError(
                "ArmVMGDBConcreteTarget write_memory at %x value %s exception %s" % (address, str(value), e))

    def read_register(self, register, **kwargs):
        try:
            # arm_target_log.debug("ArmVMGDBConcreteTarget read_register at %s "%(register))
            register_value = self.target.read_register(register)
        except Exception as e:
            # arm_target_log.debug("ArmVMGDBConcreteTarget read_register %s exception %s %s "%(register,type(e).__name__,e))
            raise SimConcreteRegisterError("ArmVMGDBConcreteTarget can't read register %s exception %s" % (register, e))
        # when accessing xmm registers and ymm register gdb return a list of 4/8 32 bit values
        # which need to be shifted appropriately to create a 128/256 bit value
        if type(register_value) is list:
            i = 0
            result = 0
            for val in register_value:
                cur_val = val << i * 32
                result |= cur_val
                i += 1
            return result
        else:
            return register_value

    def write_register(self, register, value, **kwargs):
        try:
            arm_target_log.debug("ArmVMGDBConcreteTarget write_register at %s value %x " % (register, value))
            res = self.target.write_register(register, value)
            if not res:
                arm_target_log.warning(
                    "ArmVMGDBConcreteTarget write_register failed reg %s value %x " % (register, value))
                raise SimConcreteRegisterError(
                    "ArmVMGDBConcreteTarget write_register failed reg %s value %x " % (register, value))
        except Exception as e:
            arm_target_log.warning(
                "ArmVMGDBConcreteTarget write_register exception write reg %s value %x %s " % (register, value, e))
            raise SimConcreteRegisterError(
                "ArmVMGDBConcreteTarget write_register exception write reg %s value %x %s " % (register, value, e))

    def set_breakpoint(self, address, **kwargs):
        """
        Inserts a breakpoint

        :param int address: The address at which to set the breakpoint
        :param optional bool hardware: Hardware breakpoint
        :param optional bool temporary:  Tempory breakpoint
        :param optional str regex:     If set, inserts breakpoints matching the regex
        :param optional str condition: If set, inserts a breakpoint with the condition
        :param optional int ignore_count: Amount of times the bp should be ignored
        :param optional int thread:    Thread cno in which this breakpoints should be added
        :raise angr.errors.ConcreteBreakpointError:
        """
        # arm_target_log.debug("ArmVMGDBConcreteTarget set_breakpoint at %x "%(address))
        res = self.target.set_breakpoint(address, **kwargs)
        if res == -1:
            raise SimConcreteBreakpointError("ArmVMGDBConcreteTarget failed to set_breakpoint at %x" % (address))

    def remove_breakpoint(self, address, **kwargs):
        # arm_target_log.debug("ArmVMGDBConcreteTarget remove_breakpoint at %x "%(address))
        res = self.target.remove_breakpoint(address, **kwargs)
        if res == -1:
            raise SimConcreteBreakpointError("ArmVMGDBConcreteTarget failed to set_breakpoint at %x" % (address))

    def set_watchpoint(self, address, **kwargs):
        """
        Inserts a watchpoint

        :param address: The name of a variable or an address to watch
        :param optional bool write:    Write watchpoint
        :param optional bool read:     Read watchpoint
        :raise angr.errors.ConcreteBreakpointError
        """
        arm_target_log.debug("gdb target set_watchpoing at %x value", address)
        res = self.target.set_watchpoint(address, **kwargs)
        if res == -1:
            raise SimConcreteBreakpointError("ArmVMGDBConcreteTarget failed to set_breakpoint at %x" % (address))

    def get_mappings(self):
        """
        Returns the mmap of the concrete process
        :return:
        """

        arm_target_log.debug("getting the vmmap of the concrete process")
        # mapping_output = self.target.protocols.memory.get_mappings()
        mapping_output = self.get_target_mappings()

        mapping_info_str = mapping_output.split("\n")[7:]

        _mapping_output = []
        for map in mapping_info_str:
            if len(map) > 1:
                _mapping_output.append(map)

        vmmap = []

        for map in _mapping_output:
            # map = map.split(" ")

            # removing empty entries
            # map = list(filter(lambda x: x not in ["\\t", "\\n", ''], map))
            _unk_map_name = "[unk]"

            try:
                _match = re.search(
                    r'\s*(?P<map_start_address>\S+)\s*(?P<map_end_address>\S+)\s*(?P<map_size>\S+)\s*(?P<offset>\S+)\s*(?P<permission>\S+)\s*(?P<map_name>\S*)',
                    map)
                if _match is not None:
                    map_start_address = _match.group("map_start_address")
                    map_end_address = _match.group("map_end_address")
                    offset = _match.group("offset")
                    map_name = _match.group("map_name")
                    arm_target_log.debug(f"{map_start_address} {map_end_address} {offset}: {map_name}")
                    if len(map_name) < 1:
                        map_name = _unk_map_name
                    _unk_map_name = map_name
                    vmmap.append(CustomMemoryMap(int(map_start_address, 16),
                                                 int(map_end_address, 16), int(offset, 16), map_name))
                # map_start_address = map[0].replace("\\n", '')
                # map_start_address = map_start_address.replace("\\t", '')
                # map_start_address = int(map_start_address, 16)
                # map_end_address = map[1].replace("\\n", '')
                # map_end_address = map_end_address.replace("\\t", '')
                # map_end_address = int(map_end_address, 16)
                # offset = map[3].replace("\\n", '')
                # offset = offset.replace("\\t", '')
                # offset = int(offset, 16)
                # map_name = map[4].replace("\\n", '')
                # map_name = map_name.replace("\\t", '')
                # map_name = os.path.basename(map_name)
                # vmmap.append(MemoryMap(map_start_address, map_end_address, offset, map_name))
            except (IndexError, ValueError) as e:
                # arm_target_log.debug("Can't process this vmmap entry")
                arm_target_log.debug(f"Can't process this vmmap entry: {e}")
                pass

        return vmmap

    def is_running(self):
        return self.target.get_status() == TargetStates.RUNNING

    def stop(self):
        self.target.stop()

    def shutdown(self):
        self.target.shutdown()

    def step(self, blocking=False):
        """
        Tell the target to advance one 'step'
        Note that, unlike angr, concrete targets typically operate at the granularity of single instructions
        :return:
        """
        self.target.step(blocking)

    def run(self):
        """
        Resume the execution of the target
        :return:
        """
        if not self.is_running():
            arm_target_log.debug("gdb target run")
            # pc = self.read_register('pc')
            # print("Register before resuming: %#x" % pc)
            self.target.cont()
            self.target.wait()
        else:
            arm_target_log.debug("gdb target is running!")

    def gdb_do_finish(self):
        return self.target.do_finish()

    def gdb_wait_target(self):
        return self.target.wait()

    def get_backtrace_address(self, number=1):
        return self.target.get_backtrace_address(number)

    def read_reg_pointer_string(self, reg_name):
        """
        read string from reg_name point to
        :param reg_name:
        :return:
        """
        _message = self.target.read_reg_pointer_string(reg_name)
        return _message

    def get_target_mappings(self):
        return self.target.get_mappings()

    def set_follow_child_process(self):
        """
        set process to follow child process when fork
        :return:
        """
        return self.target.execute_cmd("set follow-fork-mode child")

    def show_gdb_var_value(self, key):
        return self.target.execute_cmd(f"show {key}")