#pragma once

#include <cmath>
#include <memory>
#include <vector>
#include <juce_core/juce_core.h>
#include "TuningTable.h"

// Parser for the Scala .scl scale format (https://huygens-fokker.org/scala/scl_format.html).
// A .scl file lists pitches relative to an implicit 1/1 root; each pitch is either a
// cents value (contains a '.') or a ratio ("3/2", or a bare integer meaning n/1).
// The last listed pitch is the interval of repetition (the "formal octave").
struct ScalaScale
{
    juce::String description;
    std::vector<double> stepCents; // stepCents[0] == 0 (the root), then each listed degree except the last
    double periodCents = 1200.0;

    int notesPerPeriod() const { return (int) stepCents.size(); }

    static std::unique_ptr<ScalaScale> parse(const juce::String& text, juce::String& error)
    {
        juce::StringArray rawLines = juce::StringArray::fromLines(text);

        // Comment lines start with '!'. All other lines (including empty ones) are
        // significant: description, then note count, then the pitches.
        juce::StringArray lines;
        for (const auto& raw : rawLines)
            if (! raw.trimStart().startsWith("!"))
                lines.add(raw.trim());

        if (lines.size() < 2)
        {
            error = "File is too short to be a Scala scale.";
            return nullptr;
        }

        auto scale = std::make_unique<ScalaScale>();
        scale->description = lines[0];

        const int count = lines[1].getIntValue();
        if (count < 1 || count > 1024)
        {
            error = "Invalid note count: " + lines[1];
            return nullptr;
        }

        if (lines.size() < 2 + count)
        {
            error = "File declares " + juce::String(count) + " notes but lists fewer.";
            return nullptr;
        }

        std::vector<double> pitches;
        for (int i = 0; i < count; ++i)
        {
            double cents = 0.0;
            if (! parsePitch(lines[2 + i], cents))
            {
                error = "Could not parse pitch line: \"" + lines[2 + i] + "\"";
                return nullptr;
            }
            pitches.push_back(cents);
        }

        // Degrees within one period: root (0 cents) plus every listed pitch except
        // the last, which is the period itself.
        scale->stepCents.push_back(0.0);
        for (int i = 0; i < count - 1; ++i)
            scale->stepCents.push_back(pitches[(size_t) i]);
        scale->periodCents = pitches.back();

        if (scale->periodCents <= 0.0)
        {
            error = "The interval of repetition must be ascending.";
            return nullptr;
        }

        return scale;
    }

    // Maps the scale across all 128 keys: baseNote becomes the root (1/1) at its
    // current frequency, ascending keys walk the degrees, repeating at the period.
    void applyToTable(TuningTable& table, int baseNote) const
    {
        const int n = notesPerPeriod();
        const double baseFreq = table.frequencyForNote(baseNote);

        for (int note = 0; note < 128; ++note)
        {
            const int k = note - baseNote;
            const int period = (int) std::floor((double) k / n);
            const int degree = k - period * n;

            const double centsFromBase = period * periodCents + stepCents[(size_t) degree];
            const double freq = baseFreq * std::pow(2.0, centsFromBase / 1200.0);
            const double standard = 440.0 * std::pow(2.0, (note - 69) / 12.0);

            table.setCents(note, (float) (1200.0 * std::log2(freq / standard)));
        }
    }

private:
    static bool parsePitch(const juce::String& line, double& cents)
    {
        // The pitch is the first token; anything after whitespace is a comment.
        auto token = line.initialSectionNotContaining(" \t");
        if (token.isEmpty())
            return false;

        if (token.containsChar('.')) // cents value (may be negative)
        {
            cents = token.getDoubleValue();
            return true;
        }

        if (token.containsChar('/')) // ratio a/b (parsed as double: some historical
        {                            // scales use ratios beyond 64-bit integer range)
            const auto num = token.upToFirstOccurrenceOf("/", false, false).getDoubleValue();
            const auto den = token.fromFirstOccurrenceOf("/", false, false).getDoubleValue();
            if (num <= 0.0 || den <= 0.0)
                return false;
            cents = 1200.0 * std::log2(num / den);
            return true;
        }

        const auto num = token.getDoubleValue(); // bare integer means n/1
        if (num <= 0.0)
            return false;
        cents = 1200.0 * std::log2(num);
        return true;
    }
};
