#pragma once

#include <array>
#include <atomic>
#include <cmath>

// Per-key tuning table: a cents offset from 12-TET for each of the 128 MIDI notes.
// Read from the audio thread every block so pitch changes are heard while a note rings.
class TuningTable
{
public:
    TuningTable()
    {
        for (auto& c : cents)
            c.store(0.0f);
    }

    float getCents(int note) const
    {
        return inRange(note) ? cents[(size_t) note].load(std::memory_order_relaxed) : 0.0f;
    }

    void setCents(int note, float value)
    {
        if (inRange(note))
            cents[(size_t) note].store(value, std::memory_order_relaxed);
    }

    // "Tune all octaves": set this key and every key a whole number of octaves away.
    // keysPerOctave is how many keys it takes to reach the octave (12 on a piano), so key
    // note + j * keysPerOctave gets this key's pitch times 2^j. Offsets are cents from each
    // key's own 12-TET pitch, which works out to value + j * (1200 - 100 * keysPerOctave).
    // With 12 keys per octave that extra term is 0: every key of the pitch class gets value.
    void setCentsAllOctaves(int note, float value, int keysPerOctave = 12)
    {
        if (! inRange(note) || keysPerOctave < 1)
            return;

        if (keysPerOctave == 12) // the original behaviour, bit for bit
        {
            for (int n = note % 12; n < 128; n += 12)
                cents[(size_t) n].store(value, std::memory_order_relaxed);
            return;
        }

        const double centsPerOctave = 1200.0 - 100.0 * keysPerOctave;

        for (int n = note % keysPerOctave; n < 128; n += keysPerOctave)
        {
            const int octaves = (n - note) / keysPerOctave; // exact: n - note is a multiple of keysPerOctave
            cents[(size_t) n].store((float) ((double) value + octaves * centsPerOctave),
                                    std::memory_order_relaxed);
        }
    }

    void resetAll()
    {
        for (auto& c : cents)
            c.store(0.0f);
    }

    double frequencyForNote(int note) const
    {
        const double semitones = (note - 69) + getCents(note) / 100.0;
        return 440.0 * std::pow(2.0, semitones / 12.0);
    }

private:
    static bool inRange(int note) { return note >= 0 && note < 128; }

    std::array<std::atomic<float>, 128> cents;
};
