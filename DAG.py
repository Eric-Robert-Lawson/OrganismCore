import time
from functools import lru_cache
import symengine as se
from itertools import permutations
from math import factorial
import re
# Eric Robert Lawson Copyright 2025

"""
Getting Started
===============

1. Make sure this file is saved as `DAG.py` in your working directory.

2. Open Python in your command line or any Python shell:

    $ python

3. Import the prototype:

    >>> import DAG

4. Try these simple prototype examples:

# -------------------------------
# Multinomial expansion example: (f_0(x) + f_1(x))^3
# -------------------------------
>>> result = DAG.multinomial_DAG(3, 2, 0, DAG.unordered_combinations)
>>> result[0]
3*f0(x)*f1(x)**2 + 3*f0(x)**2*f1(x) + f0(x)**3 + f1(x)**3

# -------------------------------
# n-th derivative example: 3rd derivative of (f_0(x)*f_1(x))
# -------------------------------
>>> result = DAG.multinomial_DAG(3, 2, 1, DAG.unordered_combinations)
>>> result[0]
f0(x)*Derivative(f1(x), x, x, x) + f1(x)*Derivative(f0(x), x, x, x) + 
3*Derivative(f0(x), x)*Derivative(f1(x), x, x) + 3*Derivative(f1(x), x)*Derivative(f0(x), x, x)

# -------------------------------
# Partial Bell polynomial example: B_{3,2}^f(x)
# -------------------------------
>>> result = DAG.predefined_bell_polynomial_DAG(0, 3, 2)
>>> result[0]
3.0*Derivative(f0(x), x)*Derivative(f0(x), x, x)

# -------------------------------
# Convoluted partial Bell polynomial example: B_{3,2} over a=2 elements
# -------------------------------
>>> result = DAG.convoluted_partial_bell_polynomial(3, 2, 2)
>>> result[0]
3.0*Derivative(f0(x), x)*Derivative(f0(x), x, x) + 
3.0*Derivative(f0(x), x)*Derivative(f1(x), x, x) + 
3.0*Derivative(f1(x), x)*Derivative(f0(x), x, x) + 
3.0*Derivative(f1(x), x)*Derivative(f1(x), x, x)

# -------------------------------
# Further Resources
# -------------------------------
To understand more, see this rigorous mathematical paper:  
https://doi.org/10.5281/zenodo.17290865

I am also working on creating videos to provide additional guidance with these prototypes and next steps.

Our main goal is to create a Domain-Specific Language (DSL) to fully unlock the potential of these RDUs.  
Hopefully the requirements for this DSL are becoming clear — feel free to ask questions or contribute ideas!

"""

def sub_dag_placement(n,q,DAG,layer,structural_ordering_and_pruning_fn):
    if f"layer {layer+1}" not in DAG["legend"]:
        for node_id in DAG["legend"][f"layer {layer}"]: DAG = combinatorial_symbolic_structural_reasoning_substrate(n,q,node_id,structural_ordering_and_pruning_fn,DAG)
    return DAG

# It is important to note that q (the dimensions) and the structural ordering/pruning function are the only parameters I could see ever beeing constant amongst reasoning units.
# Otherwise DSL (Domain Specific Language) would enable this to not be hardcoded, and instead be dependent on holistic soundness or closed form. 
def combinatorial_symbolic_structural_reasoning_substrate(n, q,master_node_id,structural_combinatorial_ordering_pruning_fn,DAG=None):
    """
    General combinatorial DAG generator.
    n: total order
    q: number of dimensions
    structural_combinatorial_ordering_pruning_fn: Function that dictates ordering and pruning for a given combinatorial layer
    """
    layer = 1+layer_count(master_node_id)
    if DAG == None:
        DAG = dict()
        DAG["legend"] = dict()
    if DAG != None:
        if f"layer {layer}" not in DAG["legend"]:
            DAG["legend"][f"layer {layer}"] = dict()
    t0 = time.perf_counter()
    if type(n) != int: raise ValueError(f"n value is not integer, must be integer, not {type(n)}")
    if type(q) != int: raise ValueError(f"q value is not integer, must be integer, not {type(q)}")
    if type(master_node_id) != str:
        try:
            master_node_id = str(master_node_id)
        except Exception:
            raise ValueError(f"master_node_id value must be convertible to string! master_node_id type: {type(master_node_id)}")
    
    if type(DAG) != dict: raise ValueError(f"DAG value is not dict, must be dict, not {type(DAG)}")
    if "legend" not in DAG: DAG["legend"]=dict()    
    if master_node_id not in DAG: #only required to be done if it doesn't exist already, then how could I populate its children lol.
        DAG[master_node_id] = {
            "id": master_node_id,
            "params": {"order": n, "dimension": q},
            "children": [],
            "payload": None
        }
        params_init = dict()
        params_init["order"] = n
        params_init["dimension"] = q
        DAG["legend"]["layer 0"] = dict()
        DAG["legend"]["layer 0"][master_node_id] = params_init
    # THE REASON i AM INCLUDING THE STRUCTURE DECOMPOSED IS DUE TO CONVOLUTED PARTIAL BELL POLYNOMIAL REQUIREMENTS
    # This is where Domain Specific Language would come in handy!
    decomposed_structure = structure_decomposition(master_node_id,q)
    for Lambda_a in structural_combinatorial_ordering_pruning_fn(q,n,decomposed_structure):
        slave_node_id = master_node_id+"(" + ",".join(str(k) for k in Lambda_a) + ")"
        DAG[slave_node_id] = {
            "id": slave_node_id,
            "params": {"structural_combinatorial_ordering_pruning_fn": structural_combinatorial_ordering_pruning_fn},
            "children": [],
            "payload": {"structure": list(Lambda_a)}
        }
        params = dict()
        params["structure"] = list(Lambda_a)
        params["structural_combinatorial_ordering_pruning_fn"] = structural_combinatorial_ordering_pruning_fn
        if slave_node_id not in DAG["legend"][f"layer {layer}"]: DAG["legend"][f"layer {layer}"][slave_node_id] = dict()
        elif type(DAG["legend"][f"layer {layer}"][slave_node_id]) != dict: DAG["legend"][f"layer {layer}"][slave_node_id] = dict()
        TEMP_var =DAG["legend"][f"layer {layer}"][slave_node_id]
        TEMP_var.update(params)
        DAG["legend"][f"layer {layer}"][slave_node_id] = TEMP_var
        DAG[master_node_id]["children"].append(slave_node_id)

    t1 = time.perf_counter()
    symbolic_time = 1000 * (t1 - t0)
    print(f"{symbolic_time} milliseconds")
    return DAG

# node manipulation and traveling DAG composition, dependency pullback!
def structure_decomposition(child_id,dimension):
    matches = re.findall(r'\(([^)]+)\)', child_id)
    pullback_result = []
    for q in range(len(matches)):
        layer_result = [x for x in matches[q].split(',')]
        pullback_result += [layer_result]
    return pullback_result

def dependency_pullback_DAG(child_id,DAG):
    root_node = list(DAG["legend"]["layer 0"].keys())[0]
    dimension = DAG["legend"]["layer 0"][root_node]["dimension"]
    parent_structural_values = structure_decomposition(child_id,dimension)
    structures_list = []
    for q in range(len(parent_structural_values)):
        string_to_add = construct_node_comp(parent_structural_values[q])
        structures_list += [string_to_add]
    return [parent_structural_values,root_node,structures_list]

# Combinatorial Logic

def generate_noninc(a, k):
    """
    Partition function (creates all partitions for set of length a with k elements)
    Generate all non-increasing integer tuples of length a that sum to k.
    Order doesn't matter: (3,2,1) and (1,2,3) are considered the same sequence.
    """
    if a == 1:
        yield (k,)
    else:
        # The first element can be from 0..k, but to ensure non-increasing,
        # cap it by the previous value (initially k).
        for first in range(k, -1, -1):
            for tail in generate_noninc(a - 1, k - first):
                if first >= tail[0]:  # ensure non-increasing order
                    yield (first,) + tail

def unordered_partitions(n,q,decomposed_structure):
    return generate_noninc(n,q)

def non_zero_partitions_unordered(n,q,decomposed_structure):
    return generate_noninc_no_zeros(n,q)

def generate_noninc_no_zeros(a, k):
    """
    Generate all non-increasing integer tuples of length `a` that sum to `k`,
    with **no element being 0**.
    """
    if a == 1:
        if k > 0:  # only yield if last element is positive
            yield (k,)
        return
    # The first element must be at least 1
    for first in range(min(k - (a - 1), k), 0, -1):  # ensure enough remains for other elements
        for tail in generate_noninc_no_zeros(a - 1, k - first):
            if first >= tail[0]:  # ensure non-increasing order
                yield (first,) + tail

def get_all_distinct_permutations(f_list): return [list(p) for p in set(permutations(f_list))]

def unordered_combinations(n,q,decomposed_structure):
    combination_set = []
    for Lambda_a in generate_noninc(n,q):
        for symmetry in get_all_distinct_permutations(Lambda_a):
            combination_set += [symmetry]
    return combination_set

def unordered_combinations_lesser_than(n, q, decomposed_structure):
    combination_set = []
    decomposed0 = decomposed_structure[0]
    
    for Lambda_a in generate_noninc(n, q):
        # generate all distinct permutations
        for symmetry in set(permutations(Lambda_a)):
            # early exit check
            if any(int(symmetry[i]) > int(decomposed0[i]) for i in range(len(symmetry))):
                continue
            combination_set.append(symmetry)
    
    return combination_set

def construct_node_comp(list1):
    LLambda = "("
    for m in range(len(list1)): 
        LLambda += str(list1[m]) + ","
    LLambda =LLambda[:-1]+")"
    return LLambda

def layer_count(node):
    eval_m = node
    layer = 0
    while eval_m.find("(") > -1:
            eval_m = eval_m.replace("(", "", 1)
            layer += 1
    return layer

# Mathematical and logical parameter inputs (Non-exhaustive, but explainable for customization and self-utility)
x=se.Symbol('x')
@lru_cache(maxsize=None)
def cached_factorial(n): return factorial(n)
def multinomial_coeff_for_tuple(the_tuple): return multinomial_coeff(*the_tuple)
def return_one(the_tuple): return 1
def action_GPR(coef, structure, H_func_list,child_id,DAG): return coef * se.Mul(*[se.diff(s, x, e) for s, e in zip(H_func_list, structure)])
def action_ME(coef, structure, H_func_list,child_id,DAG): return coef * se.Mul(*[s**e for s, e in zip(H_func_list, structure)])
def convert_to_multinomial_coeff(DAG,child_id):
    dependencies = dependency_pullback_DAG(child_id,DAG)
    return multinomial_coeff_for_tuple(dependencies[0][0])
def multinomial_coeff(*ks):
    n = sum(ks)
    numerator = cached_factorial(n)
    denominator = 1
    for k in ks:
        denominator *= cached_factorial(k)
    return numerator // denominator

# Bell polynomial example logic


# subdag framing
def subdag_prep(Dep_pull):
    subdag_inputs = []
    for m in range(len(Dep_pull[0][0])): subdag_inputs += [[m,Dep_pull[0][1][m],Dep_pull[0][0][m]]]
    return subdag_inputs

def subdag_prep_inv(Dep_pull):
    subdag_inputs = []
    for m in range(len(Dep_pull[0][0])): subdag_inputs += [[m,Dep_pull[0][0][m],Dep_pull[0][1][m]]]
    return subdag_inputs

def structure_itself(Dep_pull):
    subdag_inputs = []
    for m in range(len(Dep_pull[0])): subdag_inputs += [[m,Dep_pull[0][m]]]
    return subdag_inputs

def add_transformation_fn(acc,term,node_structure):
    return acc+term



# WE MUST REFEACTOR THIS CODE BEFORE RELEASING TO PUBLIC TO MAKE IT EASIER TO UNDERSTAND!
def collect_from_layer(
    DAG, layer, subdag_fn, term_fn, collect_fn, transform_func, init_value=0, verbose=False
):
    """
    Perform a layer-wise collection on a DAG of reasoning DNA units.

    Args:
        DAG (dict): The DAG structure.
        layer (int): Layer to operate on.
        subdag_fn (callable): Maps node dependencies into sub-structures.
        term_fn (callable): Computes terms from subdag inputs.
        collect_fn (callable): Aggregates sub-terms into a node term.
        transform_func (callable): Updates the accumulator with node term.
        init_value: Initial value of the accumulator. 
        Note: In this prototype implementation, the accumulator is numerical. 
        In the DSL version, this will generalize to symbolic or structural values.
        verbose (bool): Whether to print debug info.

    Returns:
        tuple: (accumulator, updated DAG)
    """
    t0 = time.perf_counter()
    acc = init_value

    if not isinstance(DAG, dict):
        raise ValueError(f"DAG must be a dict, got {type(DAG)}")

    root_node = list(DAG["legend"]["layer 0"].keys())[0]
    dimension = DAG["legend"]["layer 0"][root_node]["dimension"]

    def expand_subdag(child_id, Dep_pull):
        """Return sub_term_set and updated DAG for one child node."""
        subdag_inputs = subdag_fn(Dep_pull)
        if verbose:
            print(f"Subdag inputs for {child_id}: {subdag_inputs}")

        sub_term_set = []
        node_structure = structure_decomposition(child_id, dimension)

        for inputs in subdag_inputs:
            children_node = f"{child_id}S({','.join(map(str, inputs))})"
            DAG[child_id]["children"].append(children_node)
            try:
                sub_term = term_fn(inputs)
            except TypeError:
                
                sub_term = term_fn(*inputs)
            sub_term_set.append(sub_term)
            DAG[children_node] = {
                "id": children_node,
                "rule": "sub-structure",
                "params": {"sub_struct": inputs, "term_fn": term_fn, "sub_term": sub_term},
                "children": [],
                "payload": None,
            }

        return sub_term_set, node_structure

    for node_id in DAG["legend"].get(f"layer {layer}", {}):
        for child_id in DAG[node_id]["children"]:
            node = DAG[child_id]
            payload = node.get("payload", {})
            structure = payload.get("structure", [])
            params = {"structure": structure}

            layer_index = layer_count(child_id)
            Dep_pull = dependency_pullback_DAG(child_id, DAG)

            # Expand subdag and compute terms
            try:
                sub_term_set, node_structure = expand_subdag(child_id, Dep_pull)
            except Exception as e:
                raise ValueError(f"Error in subdag expansion at {structure}: {e}")

            # Collect node term
            try:
                term = collect_fn(sub_term_set, node_structure)
                params.update({"collect_fn": collect_fn, "term": term})
            except Exception as e:
                raise ValueError(f"Error in term collection at {structure}: {e}")

            # Update accumulator
            try:
                acc = transform_func(acc, term, node_structure)
                params.update({"transform_func": transform_func, "acc": acc})
            except Exception as e:
                raise ValueError(f"Error in transform function at {structure}: {e}")

            # Update DAG legend
            DAG["legend"].setdefault(f"layer {layer_index}", {})
            DAG["legend"][f"layer {layer_index}"].setdefault(child_id, {})
            DAG["legend"][f"layer {layer_index}"][child_id].update(params)

    if verbose:
        symbolic_time = 1000 * (time.perf_counter() - t0)
        print(f"{symbolic_time:.3f} milliseconds")

    return acc, DAG

def collect_from_layer_root_dependent(
    DAG, layer, subdag_fn, term_fn, collect_fn, transform_func, init_value=0, verbose=False
):
    """
    Perform a layer-wise collection on a DAG with root-dependent context.

    Args:
        DAG (dict): The DAG structure.
        layer (int): Layer to operate on.
        subdag_fn (callable): Maps node dependencies into sub-structures.
        term_fn (callable): Computes terms from subdag inputs (root-dependent).
        collect_fn (callable): Aggregates sub-terms into a node term.
        transform_func (callable): Updates the accumulator with node term.
        init_value: Initial value of the accumulator. 
        Note: In this prototype implementation, the accumulator is numerical. 
        In the DSL version, this will generalize to symbolic or structural values.
        verbose (bool): Whether to print debug info.

    Returns:
        tuple: (accumulator, updated DAG)
    """
    t0 = time.perf_counter()
    acc = init_value

    if not isinstance(DAG, dict):
        raise ValueError(f"DAG must be a dict, got {type(DAG)}")

    root_node = list(DAG["legend"]["layer 0"].keys())[0]
    dimension = DAG["legend"]["layer 0"][root_node]["dimension"]

    def expand_subdag_root(child_id, Dep_pull):
        """
        Return sub_term_set and updated DAG for one child node, including root-dependent context.
        """
        subdag_inputs = subdag_fn(Dep_pull)
        if verbose:
            print(f"Subdag inputs for {child_id}: {subdag_inputs}")
            print(f"Root context: {Dep_pull[1]}")
            print()

        sub_term_set = []
        node_structure = structure_decomposition(child_id, dimension)

        for inputs in subdag_inputs:
            children_node = f"{child_id}S({','.join(map(str, inputs))})"
            DAG[child_id]["children"].append(children_node)

            # root-dependent term computation
            try:
                sub_term = term_fn([Dep_pull[1]] + inputs[1:])
            except TypeError:
                sub_term = term_fn(Dep_pull[1], *inputs[1:])

            sub_term_set.append(sub_term)
            DAG[children_node] = {
                "id": children_node,
                "rule": "sub-structure",
                "params": {"sub_struct": inputs, "term_fn": term_fn, "sub_term": sub_term},
                "children": [],
                "payload": None,
            }

        return sub_term_set, node_structure

    for node_id in DAG["legend"].get(f"layer {layer}", {}):
        for child_id in DAG[node_id]["children"]:
            node = DAG[child_id]
            payload = node.get("payload", {})
            structure = payload.get("structure", [])
            params = {"structure": structure}

            layer_index = layer_count(child_id)
            Dep_pull = dependency_pullback_DAG(child_id, DAG)

            # Expand subdag with root-dependent context
            try:
                sub_term_set, node_structure = expand_subdag_root(child_id, Dep_pull)
            except Exception as e:
                raise ValueError(f"Error in subdag expansion at {structure}: {e}")

            # Collect node term
            try:
                term = collect_fn(sub_term_set, node_structure)
                params.update({"collect_fn": collect_fn, "term": term})
            except Exception as e:
                raise ValueError(f"Error in term collection at {structure}: {e}")

            # Update accumulator
            try:
                acc = transform_func(acc, term, node_structure)
                params.update({"transform_func": transform_func, "acc": acc})
            except Exception as e:
                raise ValueError(f"Error in transform function at {structure}: {e}")

            # Update DAG legend
            DAG["legend"].setdefault(f"layer {layer_index}", {})
            DAG["legend"][f"layer {layer_index}"].setdefault(child_id, {})
            DAG["legend"][f"layer {layer_index}"][child_id].update(params)

    if verbose:
        symbolic_time = 1000 * (time.perf_counter() - t0)
        print(f"{symbolic_time:.3f} milliseconds")

    return acc, DAG


# arbitrary function application, but can be altered to any other application
def predefined_bell_polynomial_DAG(a,n,k):
    if int(k)==0:
        if int(n)==0: return [1,"Bell Polynomial 0,0 = 1"]
        else: return [0, "Bell Polynomial n,0 = 0"]
    if int(n) == 0: return [0, "Bell Polynomial 0,k = 0"]
    partitions_k= combinatorial_symbolic_structural_reasoning_substrate(n,k,str(a),non_zero_partitions_unordered)
    k44=collect_from_layer(partitions_k,0,structure_itself,BP_term,add_collect,add_transformation_fn,init_value=0)
    return k44

# arbitrary function application, but can be altered to any other application
# put in this format to allow for composability easier than the above function.
def compose_predefined_bell_polynomial_DAG(a,n,k):
    if int(k)==0:
        if int(n)==0: return 1
        else: return 0
    if int(n) == 0: return 0
    partitions_k= combinatorial_symbolic_structural_reasoning_substrate(int(n),int(k),str(a),non_zero_partitions_unordered)
    k44=collect_from_layer_root_dependent(partitions_k,0,structure_itself,BP_term,add_collect,add_transformation_fn,init_value=0)
    return k44[0]/cached_factorial(int(n))

def add_collect(sub_term_set,node_structure):
    term_to_return = 0
    for m in range(len(sub_term_set)):
        term_to_return += sub_term_set[m]
    return term_to_return

def multiply_collect(sub_term_set,node_structure):
    term_to_return = 1
    for m in range(len(sub_term_set)):
        term_to_return *= sub_term_set[m]
    return term_to_return

def multiply_collect_nfactorial(sub_term_set,node_structure):
    mod_node_structure = [int(q) for q in node_structure[0]]
    try:
        term_to_return = cached_factorial(sum(*mod_node_structure))
    except Exception as e:
        term_to_return = cached_factorial(sum(mod_node_structure))
    for m in range(len(sub_term_set)):
        term_to_return *= sub_term_set[m]
    return term_to_return

# arbitrary function application, but can be altered to any other application
def BP_term(subdag_input):
    B = se.Function(f"f{subdag_input[0]}")(x)
    subdag_inputs_modified = [int(m) for m in subdag_input[1]]
    try:
        n = sum(subdag_inputs_modified)
    except Exception as e:
        n=sum(*subdag_inputs_modified)
    term_to_return = cached_factorial(n)
    already_checked = []
    for m in range(len(subdag_inputs_modified)):
        term_to_return *= (se.diff(B,x,subdag_inputs_modified[m])/(cached_factorial(subdag_inputs_modified[m])))
        if subdag_inputs_modified[m] in already_checked: continue
        already_checked+= [subdag_inputs_modified[m]]
        term_to_return *= 1/(cached_factorial(subdag_inputs_modified.count(subdag_inputs_modified[m])))
    return term_to_return

# multinomial dag approach
# for P1 use functions like unordered_partitions, unordered_combinations, etc.
# import DAG
# multinomial expansion for (f_0(x)+f_1(x)+...+f_(k-1)(x))^n
# prototype output = DAG. multinomial_DAG(n,k,0,P1)
# for n-th derivative of f_0*f_1*...*f_(k-1)
# prototype output = DAG. multinomial_DAG(n,k,1,P1)

# P1: combinatorial primitives (unordered_partitions, unordered_combinations) used for symbolic DAG generation
# combinatorial_symbolic_structural_reasoning_substrate builds the multinomial partition DAG
def multinomial_DAG(n,k,action_type,P1):
    partitions_k= combinatorial_symbolic_structural_reasoning_substrate(n,k,"Multinomial",P1)
    if action_type == 0:
        k44=collect_from_layer(partitions_k,0,structure_itself,exponential_action,add_collect,add_transformation_fn,init_value=0)
    elif action_type == 1:
        k44=collect_from_layer(partitions_k,0,structure_itself,derivative_of_product,add_collect,add_transformation_fn,init_value=0)
    elif action_type == 2:
        k44=collect_from_layer(partitions_k,0,structure_itself,weird_inverse_exponential,add_collect,add_transformation_fn,init_value=0)
    else:
        k44=collect_from_layer(partitions_k,0,structure_itself,action_type,add_collect,add_transformation_fn,init_value=0)
    return k44

def exponential_action(subdag_input):
    subdag_inputs_modified = [int(m) for m in subdag_input[1]]
    term_to_return = multinomial_coeff_for_tuple(subdag_inputs_modified) #coefficient
    already_checked = []
    for m in range(len(subdag_inputs_modified)):
        B = se.Function(f"f{m}")(x)
        term_to_return *= B**subdag_inputs_modified[m]
    return term_to_return

def weird_inverse_exponential(subdag_input):
    subdag_inputs_modified = [int(m) for m in subdag_input[1]]
    term_to_return = multinomial_coeff_for_tuple(subdag_inputs_modified) #coefficient
    already_checked = []
    for m in range(len(subdag_inputs_modified)):
        B = se.Function(f"f{m}")(x)
        if subdag_inputs_modified[m] == 0: continue
        term_to_return *= subdag_inputs_modified[m]**B
    return term_to_return

def derivative_of_product(subdag_input):    
    subdag_inputs_modified = [int(m) for m in subdag_input[1]]
    term_to_return = multinomial_coeff_for_tuple(subdag_inputs_modified) #coefficient
    already_checked = []
    for m in range(len(subdag_inputs_modified)):
        B = se.Function(f"f{m}")(x)
        term_to_return *= se.diff(B,x,subdag_inputs_modified[m])
    return term_to_return

# a represents the number of arbitrary functions to convolute over
# The mathematical representation of convoluted partial bell polynomial is:
# \[
# B_{n,k}^{\Lambda_a}(x) = \sum_{|\Psi_a|=n} \binom{n}{\Psi_a} \prod_{v=1}^a B_{\psi_v, \lambda_v}^{f_v}(x).
# \]
# This structure has manifested in my own mathematical research, and is why it was so easy to implement. This framework was derived from my mathematical work in spirit. Therefore this implementation was the easiest for me to implement considering my conceptual background.

# Here, each node in the DAG represents a B_{psi_v, lambda_v}^{f_v}(x) term,
# and layer collection/aggregation implements the outer summation over |Psi_a| = n.
# The convolution comes from chaining outputs across layers according to the RDU framework.

# Note: full comprehension of convoluted Bell polynomials is not required to run this prototype.
# Users may experiment with inputs and observe traceable outputs through the RDU DAG.
def convoluted_partial_bell_polynomial(n,k,a):
    # we will have a elements or dimensions, n and k is based on order.
    # so we will compose of layering for n and k with a dimensions, then do convoluted partial bell polynomial!
    combinations_n= combinatorial_symbolic_structural_reasoning_substrate(n,a,str(a),unordered_combinations)
    combinations_nk = sub_dag_placement(k,a,combinations_n,1,unordered_combinations_lesser_than) 
    k44=collect_from_layer(combinations_nk,1,subdag_prep_inv,compose_predefined_bell_polynomial_DAG,multiply_collect_nfactorial,add_transformation_fn,init_value=0)
    return k44



