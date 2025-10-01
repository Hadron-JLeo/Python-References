""" "Decibel" Too loud exercise """


def too_loud(level: int, earphones: bool) -> bool:
    """Determine if the sound level is too loud, depending on earphone usage. True -> Too loud """
    
    if earphones:
        # Check if we are above 120db while wearing earphones,
        return 120 < level
    else:
        # Our limit without earphones is 70
        return 70 < level

def main()->None:
  lvl = 121
  ear = True

  x = too_loud(lvl, ear)
  print(x)

if __name__ == "__main__":
  main()
