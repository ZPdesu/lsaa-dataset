#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits.h>
#include <float.h>
#include <time.h>
#include <omp.h>


#define dprint(expr) printf(#expr " = %g \n", (double) expr)

double relative_entropy(double r, double p)
{
    return r*log(r/p)+(1-r)*log((1-r)/(1-p));
}

void  mnf_intervals(double * histo, int L, double epsilon, int ** intervals, int * Nintervals, double ** H)
{
    double * hcum = (double *)malloc(sizeof(double)*L);
    int i, M, a, b;

    *intervals = (int *)malloc(sizeof(int)*L*L*2);
    *H = (double *)malloc(sizeof(double)*L*L);
    *Nintervals = 0;

    hcum[0] = histo[0];
    for (i = 1; i < L; i++) {
        hcum[i] = hcum[i-1]+histo[i];
    }
    M = hcum[L-1];

#pragma omp parallel for schedule(dynamic) private(a, b) shared(intervals, H, Nintervals)

    for (a = 0; a < L; a++)
        for (b = a; b < L; b++) {
            double p = (double)(b-a+1)/(double)L, r;
            int nsamples;

            if (a > 0)
                nsamples = hcum[b]-hcum[a-1];
            else
                nsamples = hcum[b];
            r = (double)nsamples/(double)M;
            if (r > p) {
                double e = relative_entropy(r, p);
                if (e > log((double)L*(L+1)/2/epsilon)/(double)M) {
#pragma omp critical
                    {
                        (*intervals)[2*(*Nintervals)+0] = a+1;
                        (*intervals)[2*(*Nintervals)+1] = b+1;
                        (*H)[*Nintervals] = e;
                        *Nintervals = *Nintervals + 1;
                    }
                }
            }
        }

    free(hcum);
}

void  mnf_gaps(double * histo, int L, double epsilon, int ** gaps, int * Ngaps, double ** H)
{
    double * hcum = (double *)malloc(sizeof(double)*L);
    int i, M, a, b;

    *gaps = (int *)malloc(sizeof(int)*L*L*2);
    *H = (double *)malloc(sizeof(double)*L*L);
    *Ngaps = 0;

    hcum[0] = histo[0];
    for (i = 1; i < L; i++) {
        hcum[i] = hcum[i-1]+histo[i];
    }
    M = hcum[L-1];

#pragma omp parallel for schedule(dynamic) private(a, b) shared(gaps, H, Ngaps)

    for (a = 0; a < L; a++)
        for (b = a; b < L; b++) {
            double p = (double)(b-a+1)/(double)L, r;
            int nsamples;

            if (a > 0)
                nsamples = hcum[b]-hcum[a-1];
            else
                nsamples = hcum[b];
            r = (double)nsamples/(double)M;
            if (r < p) {
                double e = relative_entropy(r, p);
                if (e > log((double)L*(L+1)/2/epsilon)/(double)M) {
#pragma omp critical
                    {
                        (*gaps)[2*(*Ngaps)+0] = a+1;
                        (*gaps)[2*(*Ngaps)+1] = b+1;
                        (*H)[*Ngaps] = e;
                        *Ngaps = *Ngaps + 1;
                    }
                }
            }
        }

    free(hcum);
}

void mnf_modes(int * intervals, int Nintervals, double * Hintervals, int * gaps, int Ngaps, int ** modes, int * Nmodes, double ** Hmodes)
{
    int i;

    *modes = (int *)malloc(sizeof(int)*Nintervals*2);
    *Hmodes = (double *)malloc(sizeof(double)*Nintervals);
    *Nmodes = 0;

#pragma omp parallel for schedule(dynamic) private(i) shared(modes, Hmodes, Nmodes)

    for (i = 0; i < Nintervals; i++) {
        int found = 0;
        int j = 0;
        while (j < Ngaps && found == 0) {
            if (gaps[2*j+0] >= intervals[2*i+0] && gaps[2*j+1] <= intervals[2*i+1])
                found = 1;
            j = j+1;
        }
        if (found == 0) {
#pragma omp critical
            {
                (*modes)[2*(*Nmodes)+0] = intervals[2*i+0];
                (*modes)[2*(*Nmodes)+1] = intervals[2*i+1];
                (*Hmodes)[*Nmodes] = Hintervals[i];
                *Nmodes = *Nmodes + 1;
            }
        }
    }
}

void max_mnf_modes(int * modes, int Nmodes, double * Hmodes, int ** max_modes, int * Nmax_modes, double ** Hmax_modes)
{
    int i;

    *max_modes = (int *)malloc(sizeof(int)*Nmodes*2);
    *Hmax_modes = (double *)malloc(sizeof(double)*Nmodes);
    *Nmax_modes = 0;

#pragma omp parallel for schedule(dynamic) private(i) shared(max_modes, Hmax_modes, Nmax_modes)

    for (i = 0; i < Nmodes; i++) {
        int found = 0;
        int j = 0;
        while (j < Nmodes && found == 0) {
            if (j != i && modes[2*j+0] >= modes[2*i+0] && modes[2*j+1] <= modes[2*i+1] && Hmodes[j] > Hmodes[i])
                found = 1;
            j = j+1;
        }
        if (found == 0) {
            int j = 0;
            while (j < Nmodes && found == 0) {
                if (j != i && modes[2*i+0] >= modes[2*j+0] && modes[2*i+1] <= modes[2*j+1] && Hmodes[j] > Hmodes[i])
                    found = 1;
                j = j+1;
            }
            if (found == 0) {
#pragma omp critical
                {
                    (*max_modes)[2*(*Nmax_modes)+0] = modes[2*i+0];
                    (*max_modes)[2*(*Nmax_modes)+1] = modes[2*i+1];
                    (*Hmax_modes)[*Nmax_modes] = Hmodes[i];
                    *Nmax_modes = *Nmax_modes + 1;
                }
            }
        }
    }
}


int mnf(double *histo, int N, double epsilon, double *outArray1, double *outArray2)
{
    int i, Nout, Nintervals, Ngaps, Nmodes, Nmax_modes;
//    double *histo;
    int *intervals, *gaps, *modes, *max_modes;
    double *Hintervals, *Hgaps, *Hmodes, *Hmax_modes;

    /* check that number of rows in first input argument is 1 */
    // dprint(histo[5]);
    mnf_intervals(histo, N, epsilon, &intervals, &Nintervals, &Hintervals);
//    dprint(Nintervals);
    mnf_gaps(histo, N, epsilon, &gaps, &Ngaps, &Hgaps);
    /*dprint(Ngaps);*/
    mnf_modes(intervals, Nintervals, Hintervals, gaps, Ngaps, &modes, &Nmodes, &Hmodes);
    /*dprint(Nmodes);*/
    max_mnf_modes(modes, Nmodes, Hmodes, &max_modes, &Nmax_modes, &Hmax_modes);
    /*dprint(Nmax_modes);*/

    Nout = Nmax_modes;

    for (i = 0; i < Nout; i++) {
        outArray1[0*Nout+i] = max_modes[2*i+0];
        outArray1[1*Nout+i] = max_modes[2*i+1];
    }
    for (i = 0; i < Nout; i++) {
        outArray2[i] = Hmax_modes[i];
    }
    return Nout;
}