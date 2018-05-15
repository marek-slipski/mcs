#!env/bin python
# Marek Slipski
# 20170629

import pandas as pd
import numpy as np


################################################################################
# Functions to compute temperature and pressure from density profiles
# ***** add a tempeature parser that takes species, snowden args, etc -
# then I think the function arguments can be removed and those parsed values
# will be global...
################################################################################

#Some constants
g = 3.81 #m/s^2 surface gravity
M_Mars =  0.64171e+24 #kg
R_Mars = 3396.2e+3 #m
Grav = 6.67408e-11 #m^3 kg^-1 s^-2
amu = 1.660539040e-27 #kg
kboltz = 1.38064852e-23 #J/K

################################################################################
# Pressure - temperature functions, Snowden method, etc
################################################################################
def x_to_T(slope,mass):
    '''
    Convert slope of log of density (from fit) to a temperature.
    The slope is the negative recipricol of the scale height

    Inputs
    ------
    slope:
    mass: atmoic (amu)

    Outputs
    -------
    T: Temperature in Kelvin
    '''

    g = 3.71/1000 #km/s^2
    kboltzkm = kboltz/1000**2 #boltzmann constant (km^2 kg s^-2 K^-1)
    return (slope**-1*-1)*(mass*amu*g/kboltzkm)

def top_T_from_H(alt,num_den,mw,npts=9,winsize=3):
    '''
    alt: descending, km
    num_den: from top
    '''
    rollfit = pd.stats.ols.MovingOLS(
                                    x=alt[:npts],y=np.log(num_den[:npts]),
                                    window_type='rolling',window=winsize
                                    )
    Temps = rollfit.beta['x'].apply(x_to_T,args=[mw])
    return Temps

def Press_Hydro_Int(alt,num_den,mw,P0=1.e-11):
    '''
    Integrate the hydrostatic equilibrium equation for a given species using
    number densities from a given altitude in the atmosphere downward
    to determine the pressure at each point.

    alt and num_den should be cleaned up in anyway prior to fnc call

    Snowden et al. 2013, dx: 10.1016/j.icarus.2013.06.006

    Inputs
    ------
    alt: array (n), altitudes in km descending from highest to lowest
    num_den: array (n), number density of a single species
    mw: float, molecular weight of species in amu
    P0: float, integration constant, pressure at upper boundary

    Outputs
    -------
    P: array, Pressure [n] in Pascals at each r_(i+1)
    '''
    alt = np.array(alt)*1.e+3 #make array and convert to m
    num_den = np.array(num_den)*1.e+6 #make array and convert to m^-3

    r_alt = R_Mars+alt #convert alts to radius (m)
    R_0 = r_alt.max() #upper boundary
    x_alt = R_0/r_alt - 1
    mass = mw*amu #kg

    #integrate through x vals
    P = np.zeros(len(alt)-1) #initialize Pressure array
    Nx_sum = 0 #initialize sum
    for i, x in enumerate(x_alt[:-1]):
        dx = x_alt[i+1] - x
        N_mid = np.mean([num_den[i+1],num_den[i]])
        Nx_sum += N_mid*dx #summation
        P[i] = P0 + Grav*M_Mars*mass/R_0*(Nx_sum) #integrated value
    return P

def PNT(Press=None,Temp=None,Num=None):
    if Temp == None:
        return np.array(Press)/(kboltz*np.array(Num)) #Temp
    elif Press == None:
        return np.array(Temp)*kboltz*np.array(Num) #Pressure

def main_THydro(alt,num_den,mw,npts=7,winsize=3,topTmax=800.):
    '''
    alt: km descending
    num_den: cm^-3
    '''
    topT = top_T_from_H(alt,num_den,mw,npts,winsize) #get temps from H fit near top
    T0l = [topT.min(),topT.max()] #only worry abut min and max temps
    if T0l[-1] > topTmax:
        T0l[-1] = topTmax
    if T0l[0]<0:
        T0l[0] = 0.
    P0l = [PNT(Temp=t0,Num=num_den[0:1]*1.e+6) for t0 in T0l] #get Press BCs
    Pprofs = [Press_Hydro_Int(alt,num_den,mw,P0=p0) for p0 in P0l] #get P profiles
    Tprofs = [PNT(Press=Pp,Num=num_den[1:]*1.e+6) for Pp in Pprofs] #and T profs
    PTdf = pd.DataFrame(
                {'alt':alt[1:],'den':num_den[1:],'Tmin':Tprofs[0],
                'Tmax':Tprofs[1],'Pmin':Pprofs[0],'Pmax':Pprofs[1]})
    return PTdf

def restrict_PTdf(PTdf,diff_Temp,trim_km=5.):
    '''
    Take in PT DataFrame (output of main_THydro), reduce to only where Temps
    agree, compute mean.
    '''
    res = PTdf[np.abs(PTdf['Tmax']-PTdf['Tmin'] < diff_Temp)]
    newT = res[['Tmin','Tmax']].mean(axis=1)
    newP = res[['Pmin','Pmax']].mean(axis=1)
    newdf =  pd.DataFrame({'alt':res['alt'],'Pres':newP,'Temp':newT})
    newdf = newdf[newdf['alt']>=newdf['alt'].min()+trim_km]
    return newdf

def quick_T(filename):
    df = rr.IO(rr.sp_profile(filename,'Ar'),'I') #Inbound, Argon profiles
    df['sg_Ar'] = rr.savgol_density(df['abundance']) #smooth density profile
    T_df =  main_THydro(df['alt'],df['sg_Ar'],40.,npts=10,winsize=5) #Snowden Temps
    final_df = restrict_PTdf(T_df,5.) #keep only where Temps agree
    return final_df

################################################################################
################################################################################

################################################################################
# Static Stability functions
################################################################################
def cp(T):
    '''
    Calculate specific heat in Mars' upper atmosphere via
    Magalhaes et al. 1999.
    cp in J/(kg K)
    '''
    return 0.0033 * T**2 -  0.2716 * T + 656.3 #from Magalhaes et al. 1999

def static_stability(alt,temp):
    '''
    Compute (dT/dz + g/cp) from a given temperature profile
    SS in K/m
    '''
    dz = np.gradient(alt)
    dTdz = np.gradient(temp,dz)
    cpz = cp(temp)

    return dTdz + g_alt(alt)/cpz

def wB_freq(alt,temp):
    '''
    N^2, enter alt in meters!
    '''
    # N^2
    # K/m * m/(s2 K) = s^-2
    return static_stability(alt,temp)*g_alt(alt)/temp

def g_alt(alt):
    return Grav*M_Mars/(R_Mars+alt)**2
################################################################################
################################################################################

def Dmol(T,numden):
    return 2.28e+19*T**0.57*np.exp(-113.6/T)*numden**-1

def Deddy(H,k,u,c,N,dudz):
    return float(k)*(u-float(c))**4/N**3*(1/(2*H)-3*dudz/(2*(u-float(c))))

def Deddy_Im(H,k,u,c,N,gamma):
    return gamma * k * (u-c)**4 * (2*H*N**3)**(-1)

def Dmol_Im(density):
    return 1.2e+20 * (density)**(-1)

def vmol(T,density):
    #density in kg m^-3
    #vmol in m^2 s-1
    return 3.128e-7*T**0.69/density

def Dissip_mol(vmol,N,kh,u,c):
    #vmol in m^2/s
    #N in /s
    #kh in km
    #u,c in m/s
    # m^2 s^-1 * s^-3 * km * s^4 m^-4 --> m^1
    return vmol*N**3/(kh*(c-u)**4)

def Dissip_lin(H,dudz,u,c,dNdz,N):
    #m^-1 + s^-1 m^-1 s^1 + s^-1 m^-1 s^1 --> m^-1
    return 1/H + 3*dudz/(c-u) + dNdz/N

################################################################################
################################################################################

def single_T_prof(fname,species,mw,inout,sg,sgwin,sgdeg,top_H_pts,top_H_win,top_T_max):
    den_df = rr.IO(rr.sp_profile(fname,species),inout) #get inbound densities of SP
    if sg: #perform Savitsky-Golay
        d2T = rr.savgol_density(den_df['abundance'],sgwin,sgdeg) #smooth densities
    else: #or don't
        d2T = den_df['abundance']
    # Calculate temperatures from 1-orbit densities of single species, see temp_fncs.py
    PT_df = main_THydro(den_df['alt'],d2T,mw,npts=top_H_pts,winsize=top_H_win,topTmax=top_T_max)
    # Only keep temps that agree from min and max calcs and above periapse
    return PT_df

################################################################################
################################################################################


#if __name__ == '__main__':
