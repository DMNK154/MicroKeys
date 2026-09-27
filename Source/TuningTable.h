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

    // Set the offset for every key sharing this note's pitch class (all Es, all Bbs, ...).
    void setCentsAllOctaves(int note, float value)
    {
        if (! inRange(note))
            return;

        for (int n = note % 12; n < 128; n += 12)
            cents[(size_t) n].store(value, std::memory_order_relaxed);
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
