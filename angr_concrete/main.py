import time
from pathlib import Path
import angr
import avatar2
import copy
from cle.loader import Backend
from .arm_targets import ArmVMGDBConcreteTarget
from angr_targets.memory_map import MemoryMap

from angr.sim_state import SimState
from .concrete import CustomConcrete
# register concrete to my custom concrete class
SimState.register_default('concrete', CustomConcrete)


class ArmVMGDBTargetWrapper(object):
    TARGET_HOSTNAME = 'localhost'

    def __init__(self, target, json_configure, avoid_func_list, finish_func_list, hook_table, thumb_mode=True, finish_address_list=[]) -> None:
        """
        just load angr project
        :param target: target binary path
        :param json_configure:
        :param thumb_mode: for arm, if True, run in thumb mode
        """
        self.target = target
        self.json_configure = json_configure
        # target info
        analysis_concrete_wrapper_log.warn(f"analyzing {target}")
        # dissasmble
        self._static_dis_factory = GhidraDisassemblerFactory(target, json_configure)
        self._arch_name = self._static_dis_factory.get_arch_name()
        self._ord_args = ordered_agument_regs[self._arch_name]
        # check thumb or arm mode
        # $cpsr & 0x20 == 1 -> thumb
        self.thumb_mode = thumb_mode
        self.check_thumb_mode_by_gdb()
        # mask for remove lowest bit
        self._bits = self._static_dis_factory.get_bits()
        self._arch_addr_mask = 2 ** self._bits - 2
        # init static project to get some info
        # self._static_proj_factory = StaticProjectRouteFactory(target)
        # get functions to avoid from fucntion name list
        func_avoid_address_list = []
        _func_info: AvoidFunctionCallSinkInfo
        for _func_info in avoid_func_list:
            _func_name = _func_info.get_function_name()
            _func_plt_addr = self._static_dis_factory.get_plt_address(_func_name)
            func_avoid_address_list.append(_func_plt_addr)
        self.func_avoid_address_list = func_avoid_address_list
        # get finish point
        self._func_finish_address_list = []
        _func_info: FinishFunctionCallSinkInfo
        for _func_info in finish_func_list:
            _func_name = _func_info.get_function_name()
            _func_plt_addr = self._static_dis_factory.get_plt_address(_func_name)
            self._func_finish_address_list.append(_func_plt_addr)
        # record hook table
        self.hook_table = hook_table
        # 记录不是第一次到终点（应对循环）
        self.finish_explore = False
        # taint backend
        self.concrete_taint_backend = ConcreteTaintBackend()
        self._memory_concrete_pair_list = []
        # concrete gdb target
        self.avatar_gdb_target: ArmVMGDBConcreteTarget
        self.avatar_gdb_target = None
        # record constraint
        self.constraint_records = []

    def connect_guest_operator_server(self):
        """
        connect to guest operator server to send command or launch gdbserver in guest
        :return:
        """
        _socket_client_obj = SocketQemuGuestClient(self.json_configure)
        _socket_client_obj.connect_to_server()
        return _socket_client_obj

    def launch_gdb_server(self):
        """
        launch gdbserver in guest
        :return:
        """
        socket_client_obj = self.connect_guest_operator_server()
        # FIXME 执行后会自动关闭连接：Broken Pipe
        _target_binary, _host_gdbserver_port = socket_client_obj.connect_gdb_host(self.target)
        # 手动关闭
        socket_client_obj.close_connection()
        return _target_binary, _host_gdbserver_port

    def load_connect_concrete_target(self, run_to_main=True, custom_target_binary='', force_load_libs=[], ld_path=[]):
        """
        launch gdb server in guest and connect
        :param run_to_main: 默认跑到main函数开头
        :return:
        """
        self.finish_explore = False
        _target_binary, _host_gdbserver_port = self.launch_gdb_server()
        _avatar_gdb_target = ArmVMGDBConcreteTarget(avatar2.archs.arm.ARM, self.TARGET_HOSTNAME, _host_gdbserver_port)
        # follow child process
        _avatar_gdb_target.set_follow_child_process()
        res, out = _avatar_gdb_target.show_gdb_var_value("follow-fork-mode")
        self.avatar_gdb_target = _avatar_gdb_target
        if len(custom_target_binary) > 0 and Path(custom_target_binary).exists:
            _project = angr.Project(custom_target_binary, concrete_target=_avatar_gdb_target, ld_path=ld_path, use_sim_procedures=True)
        else:
            # FIXME auto detect target's arch
            _project = angr.Project(self.target, concrete_target=_avatar_gdb_target, ld_path=ld_path, use_sim_procedures=True)
        for _load_lib in force_load_libs:
            # load binary manually
            # with open(_load_lib, 'rb') as binary_stream:
            #     _backend_lib = Backend(_load_lib, binary_stream)
            #     _project.loader.dynamic_load(_backend_lib)
            _project.loader.dynamic_load(_load_lib)
        _entry_state = _project.factory.entry_state()
        #  controls the synchronization of the memory mapping of the program inside angr.
        _entry_state.options.add(angr.options.SYMBION_SYNC_CLE)
        _entry_state.options.add(angr.options.SYMBION_KEEP_STUBS_ON_SYNC)
        self._project = _project
        self._current_state = self._entry_state = _entry_state
        if run_to_main:
            self._current_state = self.run_main()
        return self._current_state

    def project_dynamic_load(self, lib_path):
        """
        load external library
        :param lib_path:
        :return:
        """
        self._project.loader.dynamic_load(lib_path)

    def get_current_state(self):
        return self._current_state

    def get_object_by_addr(self, addr):
        _vmmamp = self.avatar_gdb_target.get_mappings()
        for _mmap in _vmmamp:
            if _mmap.start_address <= addr and addr <= _mmap.end_address:
                return _mmap
        return None

    def run_concretly_with_breakpoint(self, function_name_list, condition=""):
        """
        run at breakpoint in gdb target
        """
        for function_bp in function_name_list:
            if isinstance(function_bp, int):
                function_bp = self.from_thumb_mode_addr(function_bp)
            # self.avatar_gdb_target.set_breakpoint(function_bp, condition=condition)
            self.avatar_gdb_target.set_breakpoint(function_bp, condition=condition, temporary=True)
        self.avatar_gdb_target.run()
        self.avatar_gdb_target.gdb_wait_target()
        self.avatar_gdb_target.wait_for_halt()
        # self.avatar_gdb_target.remove_breakpoint("all")

    def get_return_value(self):
        """
        FIXME add support for other arch
        :return:
        """
        _ret_offset = self._project.arch.ret_offset
        _arg_name = self._project.arch.register_names[_ret_offset]
        return self.avatar_gdb_target.read_register(_arg_name)

    def get_return_address(self):
        """
        get address to return
        :return:
        """
        _backtrace_address = self.avatar_gdb_target.get_backtrace_address()
        # remove all breakpoint
        # self.avatar_gdb_target.gdb_do_finish()
        # _pc = self.avatar_gdb_target.read_register("pc")
        # if _pc is not None:
            # print(f"stopped at {hex(_pc)}")
        return _backtrace_address

    def get_reg_pointer_string(self, reg_name="r0"):
        """
        read string from register point to
        :param reg_name:
        :return:
        """
        return self.avatar_gdb_target.read_reg_pointer_string(reg_name)

    def run_main(self):
        """
        run and breakpoint at main function
        :return: main function state
        """
        # Create a simulation manager to hold this exploration
        simgr = self._project.factory.simgr(self._entry_state)
        # first entry main function
        _bp_main_func_addr = self.from_thumb_mode_addr(self._static_dis_factory.get_main_function_address())
        symbion_res = simgr.use_technique(angr.exploration_techniques.Symbion(find=[_bp_main_func_addr]))
        exploration = simgr.run()
        _main_func_current_state = exploration.one_found
        # break on open
        # self.run_concretly_without_angr("open")
        # _concrete_state = self.execute_concretly(_main_func_current_state, ["open"])
        # FIXME 这里不太优雅。backtrace 第二行地址，要减去4，因为blx open指令大小为4
        # _concrete_state = self.execute_concretly(_main_func_current_state, [0x9a16-4])
        # FIXME add angrdbg here to run
        # 有bug，下断点的逻辑及其混乱，多下一个都卡
        # _concrete_state = self.execute_concretly(_main_func_current_state, _n_open_call_sites)
        self._current_state = _main_func_current_state
        return _main_func_current_state

    def sync_state(self, wait_time=1):
        """
        sync state from concrete in gdbserver
        :return:
        """
        new_state = self._current_state
        # FIXME wait target hang
        time.sleep(wait_time)
        new_state.concrete.sync()
        self._current_state = new_state
    
    def symbion_execute_concretly(self, state, address_list, memory_concretize=[], register_concretize=[], timeout=0):
        """
        run concretly and sync to symbion
        :param state:
        :param address_list:
        :param memory_concretize:
        :param register_concretize:
        :param timeout:
        :return:
        """
        if self.thumb_mode:
            address_list = self.from_thumb_mode_addr(address_list)
        simgr = self._project.factory.simgr(state)
        simgr.use_technique(angr.exploration_techniques.Symbion(find=address_list, memory_concretize=memory_concretize,
                                                                register_concretize=register_concretize, timeout=timeout))
        exploration = simgr.run()
        _current_state = exploration.stashes['found'][0]
        self._current_state = _current_state
        return _current_state

    def apply_arguments_taint(self, args_sink_list):
        """
        apply taint in args
        :param args_sink_list:
        :return:
        """
        for _arg in args_sink_list:
            # self.apply_taint_to_arg(_arg)
            _addr = self.get_argument_symbolic_addr(_arg)
            self.apply_taint(_addr)

    def apply_taint(self, addr):
        """
        apply taint in addr
        :param addr:
        :return:
        """
        self.concrete_taint_backend.refresh_project(self._project)
        self.concrete_taint_backend.apply_taint(self._current_state, addr)

    def get_arg_register_name(self, arg_offset):
        _arg_reg_offset = self._ord_args[arg_offset]
        # FIXME support other arch
        _arg_reg_offset = list(self._project.arch.argument_registers)[arg_offset]
        return self._project.arch.register_names[_arg_reg_offset]

    def get_argument_symbolic_addr(self, arg_offset):
        """
        get address of argument point to.
        FIXME add support for other arch
        :param arg_offset: offset to argument, for example: 0
        :return:
        """
        reg_name = self.get_arg_register_name(arg_offset)
        addr = getattr(self._current_state.regs, reg_name)
        return addr

    def apply_return_argument_taint(self):
        """
        apply taint in args
        :return:
        """
        addr = self.get_argument_symbolic_addr(0)
        self.apply_taint(addr)
        # self._memory_concrete_pair_list.append((addr, ))

    def check_finish_function_point(self, addr):
        """
        check explore finished
        :param addr:
        :return:
        """
        for _avoid_addr in self.func_finish_address_list:
            if _avoid_addr == addr:
                return True
                # if self.finish_explore == True:
                #     return True
                # else:
                #     self.finish_explore = True
                #     return False
        return False

    def check_avoid_function(self, addr):
        """
        check the addr to avoid
        :param addr:
        :return:
        """
        for _avoid_addr in self.func_avoid_address_list:
            if _avoid_addr == addr:
                return True
        return False

    def parse_offset_in_external_library(self, addr):
        """
        parse addr by get mappings in debugger
        :param addr:
        :return:
        """
        _mappings = self.avatar_gdb_target.get_mappings()
        _map = None
        _mapping: MemoryMap
        for _mapping in _mappings:
            if addr >= _mapping.start_address and addr < _mapping.end_address:
                _map = _mapping
                break
        # find library
        _map_name = _map.name
        _map_start_address = _map.start_address
        _map_end_address = _map.end_address
        _mapped_start_addrs = []
        for _mapping in _mappings:
            if _mapping.name == _map_name:
                _mapped_start_addrs.append(_mapping.start_address)
        _addr_offset = addr - _map_start_address
        _dis_image_base = self._static_dis_factory.get_binary_image_base(_map_name)
        return _map_start_address, _addr_offset, _dis_image_base, _map_name

    def hook_by_function_table(self):
        """
        hook some plt functions
        :return:
        """
        for name, hook_class in self.hook_table:
            print(f"hooking {name}")
            self._project.hook_symbol(name, hook_class())

    def explore_path(self, start_address):
        """
        explore path
        :param start_address: start point address
        :return:
        """
        _current_addr = start_address
        # FIXME add support for address in library
        _map_start_address, _addr_offset, _dis_image_base, _map_name = self.parse_offset_in_external_library(_current_addr)
        self.func_finish_address_list = self._func_finish_address_list
        # hook some functions
        self.hook_by_function_table()
        # clear constraint records
        self.constraint_records = []
        _current_simgr = self._project.factory.simgr(self._current_state.copy(),
                                                     save_unconstrained=True, save_unsat=True)
        # _current_simgr = self._project.factory.simgr(self._current_state,
        #                                              save_unconstrained=True, save_unsat=True)
        # self._current_state.memory.load(_target_next_block_addr, size=5)
        self.flat_explore(_current_simgr)

    def flat_explore(self, current_path: angr.SimulationManager, current_constraints_records=[]):
        """
        rec explore all path
        :param current_path:
        :param current_constraints_records: record all paths constraints
        :param is_thumb:
        :return:
        """
        # self._project.loader.all_elf_objects[1].addr_to_offset(self._current_state.addr)
        succ_path = current_path.copy().step(thumb=self.thumb_mode)
        # succ_path = current_path.step(thumb=self.thumb_mode)
        _succ_path_active_states = succ_path.active
        _succ_path_unsat_states = succ_path.unsat
        _succ_all_states = _succ_path_active_states + _succ_path_unsat_states
        # print(_succ_all_states)
        for _next_state in _succ_all_states:
            # _current_simgr.step(num_inst=1)
            _new_constraints_records = copy.deepcopy(current_constraints_records)
            _next_addr = _next_state.addr
            if self.check_avoid_function(_next_addr):
                continue
            if self.check_finish_function_point(_next_addr):
                # end
                self.constraint_records.append(_new_constraints_records)
            else:
                _next_path = self._project.factory.simgr(_next_state.copy(), save_unconstrained=True, save_unsat=True)
                self.flat_explore(_next_path, _new_constraints_records)
                # FIXME 
        if len(_succ_all_states) == 0:
            pass
        return

    def shutdown(self):
        """
        stop guest gdbserver
        """
        if self.avatar_gdb_target is not None:
            self.avatar_gdb_target.shutdown()

    def __del__(self):
        """
        close connection to gdb remote
        :return:
        """
        self.shutdown()


if __name__ == "__main__":
    target_wrapper = ArmVMGDBTargetWrapper("/tmp/httpd", json_configure)
    _concrete_main_state = target_wrapper.load_connect_concrete_target(True)
    # nvram_get function is at libnvram.so
    target_wrapper.run_concretly_with_breakpoint(["nvram_get"])
    target_wrapper.project_dynamic_load("/tmp/libnvram.so")
    target_wrapper.sync_state()
    _state = target_wrapper.get_current_state()
    _current_addr = _state.addr
    target_wrapper.explore_path(_current_addr)
