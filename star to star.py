"""
Star-Star (Y-Y) Connection Calculator
-------------------------------------
A menu-driven program for engineering students to analyse a three-phase
system with a STAR-connected source feeding a STAR-connected load.

Balanced star-star system (per-phase analysis):
    Source phase voltage    Vph = VL / sqrt(3)
    Total phase impedance   Z = Zline + Zload
    Phase (line) current    I = Vph / |Z|
    Load phase voltage      Vload = I * |Zload|
    Load line voltage       VL(load) = sqrt(3) * Vload
    Load power              P = 3 * I^2 * R_load
    Line loss               Ploss = 3 * I^2 * R_line
    Neutral current         = 0

Unbalanced 4-wire star-star (neutral wire present, zero impedance):
    Ik = Vk / (Zline + Zk)        In = Ia + Ib + Ic

Unbalanced 3-wire star-star (no neutral wire):
    Neutral shift voltage   V_N'N = (Va*Ya + Vb*Yb + Vc*Yc) / (Ya + Yb + Yc)
    Ik = (Vk - V_N'N) / (Zline + Zk)        (Ya = 1 / (Zline + Za), etc.)

Star-star three-phase transformer (Y-Y):
    VL2 = VL1 / a,   I2 = a * I1,   where a = N1 / N2 (turns ratio per phase)
"""

import cmath
import math

SQRT3 = math.sqrt(3)


# ---------------------------------------------------------------- input helpers
def get_positive_float(prompt):
    """Keep asking until the user enters a valid positive number."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("  Please enter a value greater than zero.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_nonneg_float(prompt):
    """Ask for a number that may be zero but not negative."""
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("  Please enter zero or a positive value.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_float(prompt):
    """Ask for any number (zero and negative values allowed)."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_load_impedance(label):
    """Ask for resistance and reactance of a load phase; return complex Z.
    Reactance: positive for inductive, negative for capacitive."""
    r = get_positive_float(f"  Load {label}: resistance R (ohm): ")
    x = get_float(f"  Load {label}: reactance X (ohm, - for capacitive): ")
    return complex(r, x)


def get_line_impedance():
    """Ask for the impedance of each line conductor (may be zero)."""
    print("  Line (cable) impedance per phase - enter 0 and 0 if ignored:")
    r = get_nonneg_float("  Line resistance (ohm): ")
    x = get_nonneg_float("  Line reactance (ohm): ")
    return complex(r, x)


# ------------------------------------------------------------------ core maths
def source_phase_voltages(v_l):
    """Return Van, Vbn, Vcn (ABC sequence, Van as reference)."""
    v_ph = v_l / SQRT3
    return (cmath.rect(v_ph, 0),
            cmath.rect(v_ph, math.radians(-120)),
            cmath.rect(v_ph, math.radians(120)))


def neutral_shift(voltages, impedances):
    """Millman's theorem: voltage between load neutral and source neutral."""
    admittances = [1 / z for z in impedances]
    numerator = sum(v * y for v, y in zip(voltages, admittances))
    return numerator / sum(admittances)


# ------------------------------------------------------------------- display
def show_polar(name, value, unit):
    """Print a complex quantity in polar form."""
    mag, ang = cmath.polar(value)
    print(f"  {name} = {mag:.3f} < {math.degrees(ang):.2f} deg {unit}")


def balanced_star_star():
    v_l = get_positive_float("Source line voltage VL (V): ")
    z_line = get_line_impedance()
    z_load = get_load_impedance("(each phase)")

    v_ph = v_l / SQRT3
    z_total = z_line + z_load
    i = v_ph / abs(z_total)
    v_load_ph = i * abs(z_load)
    v_load_line = SQRT3 * v_load_ph
    pf = z_load.real / abs(z_load)
    s_load = 3 * i ** 2 * abs(z_load)
    p_load = 3 * i ** 2 * z_load.real
    q_load = 3 * i ** 2 * z_load.imag
    p_loss = 3 * i ** 2 * z_line.real
    drop = (v_ph - v_load_ph) / v_ph * 100
    eff = p_load / (p_load + p_loss) * 100

    print("\n  ----- Balanced Star-Star System -----")
    print(f"  Source phase voltage    = {v_ph:.3f} V")
    print(f"  Total impedance per phase = {abs(z_total):.3f} ohm")
    print(f"  Line current = phase current = {i:.4f} A")
    print(f"  Load phase voltage      = {v_load_ph:.3f} V")
    print(f"  Load line voltage       = {v_load_line:.3f} V")
    print(f"  Voltage drop in lines   = {drop:.2f} %")
    print(f"  Load power factor       = {pf:.4f} {'lagging' if z_load.imag > 0 else 'leading' if z_load.imag < 0 else '(unity)'}")
    print(f"  Load apparent power S   = {s_load:,.2f} VA")
    print(f"  Load active power P     = {p_load:,.2f} W")
    print(f"  Load reactive power Q   = {q_load:,.2f} VAR")
    print(f"  Line power loss         = {p_loss:,.2f} W")
    print(f"  Transmission efficiency = {eff:.2f} %")
    print("  Neutral current         = 0 A (balanced load)")


def unbalanced_load(four_wire):
    v_l = get_positive_float("Source line voltage VL (V): ")
    z_line = get_line_impedance()
    print("\n  Enter the load impedance of each phase:")
    za, zb, zc = get_load_impedance("A"), get_load_impedance("B"), get_load_impedance("C")

    voltages = source_phase_voltages(v_l)
    loads = (za, zb, zc)
    totals = [z_line + z for z in loads]

    v_nn = 0 if four_wire else neutral_shift(voltages, totals)
    currents = [(v - v_nn) / zt for v, zt in zip(voltages, totals)]
    v_loads = [i * z for i, z in zip(currents, loads)]
    p_total = sum(abs(i) ** 2 * z.real for i, z in zip(currents, loads))

    title = "4-wire" if four_wire else "3-wire"
    print(f"\n  ----- Unbalanced {title} Star-Star System -----")
    for name, i in zip("abc", currents):
        show_polar(f"Line current I{name}", i, "A")
    for name, vl in zip("abc", v_loads):
        show_polar(f"Load voltage V{name}n'", vl, "V")
    if four_wire:
        show_polar("Neutral current In", sum(currents), "A")
    else:
        show_polar("Neutral shift V_N'N", v_nn, "V")
        print("  (Unequal load voltages appear because the load neutral floats.)")
    print(f"  Total load active power P = {p_total:,.2f} W")


def yy_transformer():
    v1 = get_positive_float("Primary line voltage VL1 (V): ")
    turns = get_positive_float("Primary turns per phase N1: ")
    turns2 = get_positive_float("Secondary turns per phase N2: ")
    kva = get_positive_float("Transformer rating (kVA): ")

    a = turns / turns2
    v2 = v1 / a
    i1 = kva * 1000 / (SQRT3 * v1)
    i2 = a * i1

    print("\n  ----- Star-Star Transformer -----")
    print(f"  Turns ratio a = N1/N2   = {a:.4f}")
    print(f"  Primary phase voltage   = {v1 / SQRT3:.3f} V")
    print(f"  Secondary line voltage  = {v2:.3f} V")
    print(f"  Secondary phase voltage = {v2 / SQRT3:.3f} V")
    print(f"  Rated primary current   = {i1:.3f} A")
    print(f"  Rated secondary current = {i2:.3f} A")
    print(f"  Type                    = {'Step-down' if a > 1 else 'Step-up' if a < 1 else 'Isolation'} transformer")
    print("  Line voltage ratio equals the turns ratio, with no phase shift.")


def menu():
    print("\n" + "=" * 54)
    print("        STAR-STAR CONNECTION CALCULATOR")
    print("=" * 54)
    print(" 1. Balanced star-star system (with line impedance)")
    print(" 2. Unbalanced 4-wire star-star (neutral current)")
    print(" 3. Unbalanced 3-wire star-star (neutral shift)")
    print(" 4. Star-star three-phase transformer")
    print(" 0. Exit")
    print("-" * 54)


def main():
    while True:
        menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            balanced_star_star()
        elif choice == "2":
            unbalanced_load(four_wire=True)
        elif choice == "3":
            unbalanced_load(four_wire=False)
        elif choice == "4":
            yy_transformer()
        elif choice == "0":
            print("\nThank you for using the calculator. Goodbye!")
            break
        else:
            print("  Invalid choice. Please select from the menu.")


if __name__ == "__main__":
    main()
