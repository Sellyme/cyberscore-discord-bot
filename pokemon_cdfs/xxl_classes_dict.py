#None = class size not known with certainty, assume XXL-3
#1 = XXL-1, range from 1.50x to 1.55x height
#2 = XXL-2, range from 1.50x to 1.75x height
#3 = XXL-3, range from 1.50x to 2.00x height
xxl_sizes = {
	'BULBASAUR_NORMAL': 2,
	'IVYSAUR_NORMAL': 2,
	'VENUSAUR_NORMAL': 2,
	'CHARMANDER_NORMAL': 2,
	'CHARMELEON_NORMAL': 2,
	'CHARIZARD_NORMAL': 2,
	'SQUIRTLE_NORMAL': 2,
	'WARTORTLE_NORMAL': 2,
	'BLASTOISE_NORMAL': 2, #unconfirmed
	'CATERPIE': 2,
	'METAPOD': 2, #unconfirmed
	'BUTTERFREE': 2, #unconfirmed
	'WEEDLE_NORMAL': 2,
	'KAKUNA_NORMAL': 2,
	'BEEDRILL_NORMAL': 2, #unconfirmed
	'PIDGEY': 2,
	'PIDGEOTTO': 2,
	'PIDGEOT': 2,
	'RATTATA_ALOLA': None,
	'RATTATA_NORMAL': None,
	'RATICATE_ALOLA': None,
	'RATICATE_NORMAL': None,
	'SPEAROW': 2,
	'FEAROW': 2,
	'EKANS_NORMAL': 2,
	'ARBOK_NORMAL': 2,
	'PIKACHU_NORMAL': 2,
	'RAICHU_ALOLA': None,
	'RAICHU_NORMAL': None,
	'SANDSHREW_ALOLA': None,
	'SANDSHREW_NORMAL': None,
	'SANDSLASH_ALOLA': None,
	'SANDSLASH_NORMAL': None,
	'NIDORAN_F': 2,
	'NIDORINA_NORMAL': 2, #unconfirmed
	'NIDOQUEEN_NORMAL': None,
	'NIDORAN_M': 2,
	'NIDORINO_NORMAL': 2, #unconfirmed
	'NIDOKING_NORMAL': 3,
	'CLEFAIRY': None,
	'CLEFABLE': None,
	'VULPIX_ALOLA': None,
	'VULPIX_NORMAL': 2,
	'NINETALES_ALOLA': None,
	'NINETALES_NORMAL': 3,
	'JIGGLYPUFF': 2,
	'WIGGLYTUFF': None,
	'ZUBAT_NORMAL': 2,
	'GOLBAT_NORMAL': 2,
	'ODDISH_NORMAL': 1,
	'GLOOM_NORMAL': 1,
	'VILEPLUME_NORMAL': 3,
	'PARAS': 2,
	'PARASECT': None,
	'VENONAT_NORMAL': 1,
	'VENOMOTH_NORMAL': 1,
	'DIGLETT_ALOLA': None,
	'DIGLETT_NORMAL': 3,
	'DUGTRIO_ALOLA': None,
	'DUGTRIO_NORMAL': None,
	'MEOWTH_ALOLA': None,
	'MEOWTH_GALARIAN': None,
	'MEOWTH_NORMAL': None,
	'PERSIAN_ALOLA': None,
	'PERSIAN_NORMAL': None,
	'PSYDUCK_NORMAL': 2,
	'GOLDUCK_NORMAL': None,
	'MANKEY': 2,
	'PRIMEAPE': None,
	'GROWLITHE_HISUIAN': None,
	'GROWLITHE_NORMAL': None,
	'ARCANINE_HISUIAN': None,
	'ARCANINE_NORMAL': None,
	'POLIWAG_NORMAL': 2,
	'POLIWHIRL_NORMAL': 2,
	'POLIWRATH_NORMAL': None,
	'ABRA_NORMAL': 2,
	'KADABRA_NORMAL': 2,
	'ALAKAZAM_NORMAL': None,
	'MACHOP_NORMAL': None,
	'MACHOKE_NORMAL': None,
	'MACHAMP_NORMAL': None,
	'BELLSPROUT_NORMAL': 1,
	'WEEPINBELL_NORMAL': 3,
	'VICTREEBEL_NORMAL': 3,
	'TENTACOOL': 3,
	'TENTACRUEL': 3,
	'GEODUDE_ALOLA': 2, #unconfirmed
	'GEODUDE_NORMAL': 2, #unconfirmed
	'GRAVELER_ALOLA': 2, #unconfirmed
	'GRAVELER_NORMAL': 2, #unconfirmed
	'GOLEM_ALOLA': 3,
	'GOLEM_NORMAL': None,
	'PONYTA_GALARIAN': None,
	'PONYTA_NORMAL': 2, #unconfirmed
	'RAPIDASH_GALARIAN': None,
	'RAPIDASH_NORMAL': 1, #unconfirmed
	'SLOWPOKE_GALARIAN': None,
	'SLOWPOKE_NORMAL': 2,
	'SLOWBRO_GALARIAN': None,
	'SLOWBRO_NORMAL': None,
	'MAGNEMITE_NORMAL': 3,
	'MAGNETON_NORMAL': None,
	'FARFETCHD_GALARIAN': None,
	'FARFETCHD_NORMAL': None,
	'DODUO': None,
	'DODRIO': None,
	'SEEL': 2,
	'DEWGONG': None,
	'GRIMER_ALOLA': None,
	'GRIMER_NORMAL': None,
	'MUK_ALOLA': None,
	'MUK_NORMAL': None,
	'SHELLDER_NORMAL': 2,
	'CLOYSTER_NORMAL': None,
	'GASTLY': 3,
	'HAUNTER': 3,
	'GENGAR_NORMAL': None,
	'ONIX_NORMAL': None,
	'DROWZEE_NORMAL': 2,
	'HYPNO_NORMAL': 1,
	'KRABBY_NORMAL': 2,
	'KINGLER_NORMAL': 3,
	'VOLTORB_HISUIAN': None,
	'VOLTORB_NORMAL': None,
	'ELECTRODE_HISUIAN': None,
	'ELECTRODE_NORMAL': None,
	'EXEGGCUTE_NORMAL': 3,
	'EXEGGUTOR_ALOLA': None,
	'EXEGGUTOR_NORMAL': None,
	'CUBONE_NORMAL': None,
	'MAROWAK_ALOLA': None,
	'MAROWAK_NORMAL': None,
	'HITMONLEE_NORMAL': 1,
	'HITMONCHAN_NORMAL': 1,
	'LICKITUNG': 2,
	'KOFFING_NORMAL': 3,
	'WEEZING_GALARIAN': None,
	'WEEZING_NORMAL': None,
	'RHYHORN_NORMAL': 2,
	'RHYDON_NORMAL': None,
	'CHANSEY': 2,
	'TANGELA_NORMAL': 3,
	'KANGASKHAN_NORMAL': 2,
	'HORSEA_NORMAL': None,
	'SEADRA_NORMAL': None,
	'GOLDEEN': 3,
	'SEAKING': 3,
	'STARYU': 2,
	'STARMIE': None,
	'MR_MIME_GALARIAN': None,
	'MR_MIME_NORMAL': None,
	'SCYTHER_NORMAL': None,
	'JYNX': 1,
	'ELECTABUZZ_NORMAL': None,
	'MAGMAR_NORMAL': 2,
	'PINSIR_NORMAL': 2,
	'TAUROS': 2,
	'MAGIKARP_NORMAL': 3,
	'GYARADOS_NORMAL': 3,
	'LAPRAS_NORMAL': None,
	'DITTO': None,
	'EEVEE': 2,
	'VAPOREON': 1,
	'JOLTEON': 1,
	'FLAREON': 1,
	'PORYGON_NORMAL': 3,
	'OMANYTE_NORMAL': None,
	'OMASTAR_NORMAL': None,
	'KABUTO_NORMAL': None,
	'KABUTOPS_NORMAL': None,
	'AERODACTYL_NORMAL': 3,
	'SNORLAX_NORMAL': 2,
	'ARTICUNO_GALARIAN': None,
	'ARTICUNO_NORMAL': None,
	'ZAPDOS_GALARIAN': None,
	'ZAPDOS_NORMAL': None,
	'MOLTRES_GALARIAN': None,
	'MOLTRES_NORMAL': None,
	'DRATINI_NORMAL': None,
	'DRAGONAIR_NORMAL': None,
	'DRAGONITE_NORMAL': None,
	'MEWTWO_NORMAL': None,
	'MEW': None,
	'CHIKORITA_NORMAL': None,
	'BAYLEEF_NORMAL': None,
	'MEGANIUM_NORMAL': None,
	'CYNDAQUIL_NORMAL': None,
	'QUILAVA_NORMAL': None,
	'TYPHLOSION_NORMAL': None,
	'TOTODILE_NORMAL': None,
	'CROCONAW_NORMAL': None,
	'FERALIGATR_NORMAL': None,
	'SENTRET': None,
	'FURRET': None,
	'HOOTHOOT': 2,
	'NOCTOWL': 2,
	'LEDYBA': 2,
	'LEDIAN': 2,
	'SPINARAK': 2,
	'ARIADOS': 2,
	'CROBAT_NORMAL': None,
	'CHINCHOU': 3,
	'LANTURN': 3,
	'PICHU': None,
	'CLEFFA': None,
	'IGGLYBUFF': None,
	'TOGEPI': None,
	'TOGETIC': 2,
	'NATU': 2,
	'XATU': None,
	'MAREEP_NORMAL': 2,
	'FLAAFFY_NORMAL': 2,
	'AMPHAROS_NORMAL': 2,
	'BELLOSSOM_NORMAL': 3,
	'MARILL': 2,
	'AZUMARILL': 2,
	'SUDOWOODO': 3,
	'POLITOED_NORMAL': None,
	'HOPPIP_NORMAL': 2,
	'SKIPLOOM_NORMAL': 2,
	'JUMPLUFF_NORMAL': 2,
	'AIPOM_NORMAL': 2,
	'SUNKERN': 3,
	'SUNFLORA': None,
	'YANMA': None,
	'WOOPER_NORMAL': 2,
	'QUAGSIRE_NORMAL': None,
	'ESPEON': 1,
	'UMBREON': 1,
	'MURKROW_NORMAL': 3,
	'SLOWKING_GALARIAN': None,
	'SLOWKING_NORMAL': None,
	'MISDREAVUS_NORMAL': 2,
	'WOBBUFFET_NORMAL': 2,
	'GIRAFARIG': 2,
	'PINECO_NORMAL': 2,
	'FORRETRESS_NORMAL': None,
	'DUNSPARCE': 2,
	'GLIGAR_NORMAL': None,
	'STEELIX_NORMAL': None,
	'SNUBBULL_NORMAL': 2,
	'GRANBULL_NORMAL': 2,
	'QWILFISH_HISUIAN': None,
	'QWILFISH_NORMAL': 2,
	'SCIZOR_NORMAL': None,
	'SHUCKLE_NORMAL': 2,
	'HERACROSS': None,
	'SNEASEL_HISUIAN': None,
	'SNEASEL_NORMAL': None,
	'TEDDIURSA_NORMAL': 2,
	'URSARING_NORMAL': 2,
	'SLUGMA': 2,
	'MAGCARGO': 2,
	'SWINUB_NORMAL': 2,
	'PILOSWINE_NORMAL': 2,
	'CORSOLA': None,
	'REMORAID': 2,
	'OCTILLERY': 3,
	'DELIBIRD_NORMAL': None,
	'MANTINE': 3,
	'SKARMORY_NORMAL': 3,
	'HOUNDOUR_NORMAL': 2,
	'HOUNDOOM_NORMAL': 2,
	'KINGDRA_NORMAL': None,
	'PHANPY': 3,
	'DONPHAN': None,
	'PORYGON2_NORMAL': None,
	'STANTLER_NORMAL': 2,
	'SMEARGLE': None,
	'TYROGUE': None,
	'HITMONTOP': 2,
	'SMOOCHUM': None,
	'ELEKID': None,
	'MAGBY': None,
	'MILTANK': 2,
	'BLISSEY': None,
	'RAIKOU_NORMAL': None,
	'RAIKOU_S': None,
	'ENTEI_NORMAL': None,
	'ENTEI_S': None,
	'SUICUNE_NORMAL': None,
	'SUICUNE_S': None,
	'LARVITAR_NORMAL': 2,
	'PUPITAR_NORMAL': 2,
	'TYRANITAR_NORMAL': 3,
	'LUGIA_NORMAL': None,
	'LUGIA_S': None,
	'HO_OH_NORMAL': None,
	'HO_OH_S': None,
	'CELEBI': None,
	'TREECKO': 1,
	'GROVYLE': 1,
	'SCEPTILE': None,
	'TORCHIC_NORMAL': 1,
	'COMBUSKEN_NORMAL': 1,
	'BLAZIKEN_NORMAL': None,
	'MUDKIP_NORMAL': 1,
	'MARSHTOMP_NORMAL': 1,
	'SWAMPERT_NORMAL': None,
	'POOCHYENA_NORMAL': 2,
	'MIGHTYENA_NORMAL': 2,
	'ZIGZAGOON_GALARIAN': None,
	'ZIGZAGOON_NORMAL': 2,
	'LINOONE_GALARIAN': None,
	'LINOONE_NORMAL': 2,
	'WURMPLE': 2,
	'SILCOON': None,
	'BEAUTIFLY': None,
	'CASCOON': None,
	'DUSTOX': None,
	'LOTAD': 3,
	'LOMBRE': 2,
	'LUDICOLO': 2,
	'SEEDOT_NORMAL': 2,
	'NUZLEAF_NORMAL': None,
	'SHIFTRY_NORMAL': None,
	'TAILLOW': 3,
	'SWELLOW': None,
	'WINGULL': 2,
	'PELIPPER': None,
	'RALTS_NORMAL': 2,
	'KIRLIA_NORMAL': 2,
	'GARDEVOIR_NORMAL': 1,
	'SURSKIT': 2,
	'MASQUERAIN': 2,
	'SHROOMISH': 2,
	'BRELOOM': None,
	'SLAKOTH': 2,
	'VIGOROTH': 1,
	'SLAKING': 1,
	'NINCADA': 2,
	'NINJASK': None,
	'SHEDINJA': None,
	'WHISMUR_NORMAL': 2,
	'LOUDRED_NORMAL': 2,
	'EXPLOUD_NORMAL': None,
	'MAKUHITA_NORMAL': 2,
	'HARIYAMA_NORMAL': 1,
	'AZURILL': None,
	'NOSEPASS_NORMAL': 3,
	'SKITTY': 1,
	'DELCATTY': 1,
	'SABLEYE_NORMAL': 2,
	'MAWILE_NORMAL': 2,
	'ARON_NORMAL': 3,
	'LAIRON_NORMAL': 3,
	'AGGRON_NORMAL': 3,
	'MEDITITE': 1,
	'MEDICHAM': 1,
	'ELECTRIKE_NORMAL': 2,
	'MANECTRIC_NORMAL': None,
	'PLUSLE': 2,
	'MINUN': 2,
	'VOLBEAT': 2,
	'ILLUMISE': 2,
	'ROSELIA': 2,
	'GULPIN': 3,
	'SWALOT': 3,
	'CARVANHA_NORMAL': 3,
	'SHARPEDO_NORMAL': None,
	'WAILMER': 3,
	'WAILORD': None,
	'NUMEL': 1,
	'CAMERUPT': 1,
	'TORKOAL': None,
	'SPOINK': 1,
	'GRUMPIG': 2,
	'TRAPINCH_NORMAL': 2,
	'VIBRAVA_NORMAL': None,
	'FLYGON_NORMAL': None,
	'CACNEA_NORMAL': 3,
	'CACTURNE_NORMAL': 3,
	'SWABLU': 2,
	'ALTARIA': None,
	'ZANGOOSE': 2,
	'SEVIPER': 1,
	'LUNATONE': 3,
	'SOLROCK': 3,
	'BARBOACH': 3,
	'WHISCASH': 3,
	'CORPHISH': 2,
	'CRAWDAUNT': None,
	'BALTOY': 2,
	'CLAYDOL': 2,
	'LILEEP_NORMAL': 3,
	'CRADILY_NORMAL': None,
	'ANORITH_NORMAL': 2,
	'ARMALDO_NORMAL': None,
	'FEEBAS': 3,
	'MILOTIC': None,
	'CASTFORM_NORMAL': None,
	'CASTFORM_RAINY': None,
	'CASTFORM_SNOWY': None,
	'CASTFORM_SUNNY': None,
	'KECLEON': None,
	'SHUPPET_NORMAL': 2,
	'BANETTE_NORMAL': 2,
	'DUSKULL_NORMAL': 2,
	'DUSCLOPS_NORMAL': 1,
	'TROPIUS': None,
	'CHIMECHO': 1,
	'ABSOL_NORMAL': 2,
	'WYNAUT': None,
	'SNORUNT': 2,
	'GLALIE': None,
	'SPHEAL_NORMAL': 2,
	'SEALEO_NORMAL': None,
	'WALREIN_NORMAL': None,
	'CLAMPERL': 3,
	'HUNTAIL': None,
	'GOREBYSS': None,
	'RELICANTH': None,
	'LUVDISC': 3,
	'BAGON_NORMAL': 2,
	'SHELGON_NORMAL': 2,
	'SALAMENCE_NORMAL': 3,
	'BELDUM_NORMAL': 3,
	'METANG_NORMAL': 3,
	'METAGROSS_NORMAL': 3,
	'REGIROCK': None,
	'REGICE': None,
	'REGISTEEL': None,
	'LATIAS_NORMAL': None,
	'LATIAS_S': None,
	'LATIOS_NORMAL': None,
	'LATIOS_S': None,
	'KYOGRE': None,
	'GROUDON': None,
	'RAYQUAZA': None,
	'JIRACHI': None,
	'DEOXYS_ATTACK': None,
	'DEOXYS_DEFENSE': None,
	'DEOXYS_NORMAL': None,
	'DEOXYS_SPEED': None,
	'TURTWIG_NORMAL': 1,
	'GROTLE_NORMAL': 1,
	'TORTERRA_NORMAL': None,
	'CHIMCHAR_NORMAL': 2,
	'MONFERNO_NORMAL': 2,
	'INFERNAPE_NORMAL': None,
	'PIPLUP': 2,
	'PRINPLUP': 2,
	'EMPOLEON': None,
	'STARLY_NORMAL': 2,
	'STARAVIA_NORMAL': 2,
	'STARAPTOR_NORMAL': 2,
	'BIDOOF_NORMAL': 2,
	'BIBAREL_NORMAL': None,
	'KRICKETOT': 2,
	'KRICKETUNE': None,
	'SHINX': None,
	'LUXIO': None,
	'LUXRAY': None,
	'BUDEW': None,
	'ROSERADE': None,
	'CRANIDOS': 3,
	'RAMPARDOS': None,
	'SHIELDON': 3,
	'BASTIODON': None,
	'BURMY_PLANT': 2,
	'BURMY_SANDY': 2,
	'BURMY_TRASH': 2,
	'WORMADAM_PLANT': None,
	'WORMADAM_SANDY': None,
	'WORMADAM_TRASH': None,
	'MOTHIM': None,
	'COMBEE': 2,
	'VESPIQUEN': None,
	'PACHIRISU': None,
	'BUIZEL': 2,
	'FLOATZEL': None,
	'CHERUBI': None,
	'CHERRIM_OVERCAST': 3,
	'CHERRIM_SUNNY': 3,
	'SHELLOS_EAST_SEA': 2,
	'SHELLOS_WEST_SEA': 2,
	'GASTRODON_EAST_SEA': None,
	'GASTRODON_WEST_SEA': None,
	'AMBIPOM_NORMAL': None,
	'DRIFLOON': 3,
	'DRIFBLIM': 3,
	'BUNEARY': 2,
	'LOPUNNY': 1,
	'MISMAGIUS_NORMAL': None,
	'HONCHKROW_NORMAL': None,
	'GLAMEOW': 2,
	'PURUGLY': 1,
	'CHINGLING': None,
	'STUNKY_NORMAL': 2,
	'SKUNTANK_NORMAL': 1,
	'BRONZOR': 2,
	'BRONZONG': 2,
	'BONSLY': None,
	'MIME_JR': None,
	'HAPPINY': None,
	'CHATOT': None,
	'SPIRITOMB': None,
	'GIBLE_NORMAL': None,
	'GABITE_NORMAL': None,
	'GARCHOMP_NORMAL': None,
	'MUNCHLAX': None,
	'RIOLU': None,
	'LUCARIO': None,
	'HIPPOPOTAS_NORMAL': 2,
	'HIPPOWDON_NORMAL': 1,
	'SKORUPI_NORMAL': None,
	'DRAPION_NORMAL': None,
	'CROAGUNK': 2,
	'TOXICROAK': 1,
	'CARNIVINE': None,
	'FINNEON': 3,
	'LUMINEON': 3,
	'MANTYKE': None,
	'SNOVER_NORMAL': None,
	'ABOMASNOW_NORMAL': None,
	'WEAVILE_NORMAL': None,
	'MAGNEZONE_NORMAL': None,
	'LICKILICKY': None,
	'RHYPERIOR_NORMAL': None,
	'TANGROWTH_NORMAL': None,
	'ELECTIVIRE_NORMAL': None,
	'MAGMORTAR_NORMAL': None,
	'TOGEKISS': None,
	'YANMEGA': None,
	'LEAFEON': None,
	'GLACEON': None,
	'GLISCOR_NORMAL': None,
	'MAMOSWINE_NORMAL': None,
	'PORYGON_Z_NORMAL': None,
	'GALLADE_NORMAL': None,
	'PROBOPASS_NORMAL': None,
	'DUSKNOIR_NORMAL': None,
	'FROSLASS': None,
	'ROTOM_FAN': None,
	'ROTOM_FROST': None,
	'ROTOM_HEAT': None,
	'ROTOM_MOW': None,
	'ROTOM_NORMAL': None,
	'ROTOM_WASH': None,
	'UXIE': None,
	'MESPRIT': None,
	'AZELF': None,
	'DIALGA': None,
	'PALKIA': None,
	'HEATRAN': None,
	'REGIGIGAS': None,
	'GIRATINA_ALTERED': None,
	'GIRATINA_ORIGIN': None,
	'CRESSELIA': None,
	'PHIONE': None,
	'MANAPHY': None,
	'DARKRAI': None,
	'SHAYMIN_LAND': None,
	'SHAYMIN_SKY': None,
	'ARCEUS_BUG': None,
	'ARCEUS_DARK': None,
	'ARCEUS_DRAGON': None,
	'ARCEUS_ELECTRIC': None,
	'ARCEUS_FAIRY': None,
	'ARCEUS_FIGHTING': None,
	'ARCEUS_FIRE': None,
	'ARCEUS_FLYING': None,
	'ARCEUS_GHOST': None,
	'ARCEUS_GRASS': None,
	'ARCEUS_GROUND': None,
	'ARCEUS_ICE': None,
	'ARCEUS_NORMAL': None,
	'ARCEUS_POISON': None,
	'ARCEUS_PSYCHIC': None,
	'ARCEUS_ROCK': None,
	'ARCEUS_STEEL': None,
	'ARCEUS_WATER': None,
	'VICTINI': None,
	'SNIVY': 1,
	'SERVINE': 1,
	'SERPERIOR': None,
	'TEPIG': 1,
	'PIGNITE': 1,
	'EMBOAR': None,
	'OSHAWOTT': 1,
	'DEWOTT': 1,
	'SAMUROTT': None,
	'PATRAT': 1,
	'WATCHOG': None,
	'LILLIPUP': 2,
	'HERDIER': 2,
	'STOUTLAND': 1, #unconfirmed
	'PURRLOIN': 2,
	'LIEPARD': None,
	'PANSAGE': 2,
	'SIMISAGE': None,
	'PANSEAR': 2,
	'SIMISEAR': None,
	'PANPOUR': 2,
	'SIMIPOUR': None,
	'MUNNA': 2,
	'MUSHARNA': None,
	'PIDOVE': 2,
	'TRANQUILL': 2,
	'UNFEZANT': None,
	'BLITZLE': 2,
	'ZEBSTRIKA': None,
	'ROGGENROLA': 2,
	'BOLDORE': 3,
	'GIGALITH': None,
	'WOOBAT': 2,
	'SWOOBAT': None,
	'DRILBUR': 2,
	'EXCADRILL': None,
	'AUDINO': 1,
	'TIMBURR': None,
	'GURDURR': None,
	'CONKELDURR': None,
	'TYMPOLE': 1,
	'PALPITOAD': None,
	'SEISMITOAD': None,
	'THROH': 1,
	'SAWK': None,
	'SEWADDLE': 2,
	'SWADLOON': None,
	'LEAVANNY': None,
	'VENIPEDE': 2,
	'WHIRLIPEDE': 1,
	'SCOLIPEDE': None,
	'COTTONEE': 2,
	'WHIMSICOTT': None,
	'PETILIL': 3,
	'LILLIGANT': None,
	'BASCULIN_BLUE_STRIPED': 3,
	'BASCULIN_RED_STRIPED': 3,
	'SANDILE': None,
	'KROKOROK': None,
	'KROOKODILE': None,
	'DARUMAKA_GALARIAN': None,
	'DARUMAKA_NORMAL': None,
	'DARMANITAN_GALARIAN_STANDARD': None,
	'DARMANITAN_GALARIAN_ZEN': None,
	'DARMANITAN_STANDARD': None,
	'DARMANITAN_ZEN': None,
	'MARACTUS': None,
	'DWEBBLE': 2,
	'CRUSTLE': None,
	'SCRAGGY': None,
	'SCRAFTY': None,
	'SIGILYPH': None,
	'YAMASK_GALARIAN': None,
	'YAMASK_NORMAL': None,
	'COFAGRIGUS_NORMAL': None,
	'TIRTOUGA': 3,
	'CARRACOSTA': None,
	'ARCHEN': 3,
	'ARCHEOPS': None,
	'TRUBBISH': 1,
	'GARBODOR': None,
	'ZORUA': 2,
	'ZOROARK': None,
	'MINCCINO': 2,
	'CINCCINO': None,
	'GOTHITA': 2,
	'GOTHORITA': None,
	'GOTHITELLE': None,
	'SOLOSIS': 2,
	'DUOSION': None,
	'REUNICLUS': None,
	'DUCKLETT': 2,
	'SWANNA': None,
	'VANILLITE': None,
	'VANILLISH': None,
	'VANILLUXE': None,
	'DEERLING_AUTUMN': 2,
	'DEERLING_SPRING': 2,
	'DEERLING_SUMMER': 2,
	'DEERLING_WINTER': 2,
	'SAWSBUCK_AUTUMN': None,
	'SAWSBUCK_SPRING': None,
	'SAWSBUCK_SUMMER': None,
	'SAWSBUCK_WINTER': None,
	'EMOLGA': 2,
	'KARRABLAST': 2,
	'ESCAVALIER': None,
	'FOONGUS': 3,
	'AMOONGUSS': None,
	'FRILLISH_FEMALE': None,
	'FRILLISH_NORMAL': 1,
	'JELLICENT_FEMALE': None,
	'JELLICENT_NORMAL': None,
	'ALOMOMOLA': 3,
	'JOLTIK': 1,
	'GALVANTULA': None,
	'FERROSEED': 3,
	'FERROTHORN': None,
	'KLINK': None,
	'KLANG': None,
	'KLINKLANG': None,
	'TYNAMO': 3,
	'EELEKTRIK': 3,
	'EELEKTROSS': None,
	'ELGYEM': 2,
	'BEHEEYEM': None,
	'LITWICK': None,
	'LAMPENT': None,
	'CHANDELURE': None,
	'AXEW': 2,
	'FRAXURE': None,
	'HAXORUS': None,
	'CUBCHOO_NORMAL': 1,
	'BEARTIC_NORMAL': None,
	'CRYOGONAL': None,
	'SHELMET': 2,
	'ACCELGOR': None,
	'STUNFISK_GALARIAN': None,
	'STUNFISK_NORMAL': None,
	'MIENFOO': None,
	'MIENSHAO': None,
	'DRUDDIGON': None,
	'GOLETT': 3,
	'GOLURK': None,
	'PAWNIARD': None,
	'BISHARP': None,
	'BOUFFALANT': None,
	'RUFFLET': 2,
	'BRAVIARY_HISUIAN': None,
	'BRAVIARY_NORMAL': None,
	'VULLABY': None,
	'MANDIBUZZ': None,
	'HEATMOR': None,
	'DURANT': 2,
	'DEINO': 2,
	'ZWEILOUS': 2,
	'HYDREIGON': None,
	'LARVESTA': None,
	'VOLCARONA': None,
	'COBALION': None,
	'TERRAKION': None,
	'VIRIZION': None,
	'TORNADUS_INCARNATE': None,
	'TORNADUS_THERIAN': None,
	'THUNDURUS_INCARNATE': None,
	'THUNDURUS_THERIAN': None,
	'RESHIRAM': None,
	'ZEKROM': None,
	'LANDORUS_INCARNATE': None,
	'LANDORUS_THERIAN': None,
	'KYUREM_BLACK': None,
	'KYUREM_NORMAL': None,
	'KYUREM_WHITE': None,
	'KELDEO_ORDINARY': None,
	'KELDEO_RESOLUTE': None,
	'MELOETTA_ARIA': None,
	'MELOETTA_PIROUETTE': None,
	'GENESECT_BURN': None,
	'GENESECT_CHILL': None,
	'GENESECT_DOUSE': None,
	'GENESECT_NORMAL': None,
	'GENESECT_SHOCK': None,
	'CHESPIN': 2,
	'QUILLADIN': None,
	'CHESNAUGHT': None,
	'FENNEKIN': 2,
	'BRAIXEN': 2, #unconfirmed
	'DELPHOX': 2, #unconfirmed
	'FROAKIE': 2,
	'FROGADIER': None,
	'GRENINJA': None,
	'BUNNELBY': 2,
	'DIGGERSBY': None,
	'FLETCHLING': 2,
	'FLETCHINDER': 2,
	'TALONFLAME': None,
	'SCATTERBUG_ARCHIPELAGO': None,
	'SCATTERBUG_CONTINENTAL': None,
	'SCATTERBUG_ELEGANT': None,
	'SCATTERBUG_FANCY': None,
	'SCATTERBUG_GARDEN': None,
	'SCATTERBUG_HIGH_PLAINS': None,
	'SCATTERBUG_ICY_SNOW': None,
	'SCATTERBUG_JUNGLE': None,
	'SCATTERBUG_MARINE': None,
	'SCATTERBUG_MEADOW': None,
	'SCATTERBUG_MODERN': None,
	'SCATTERBUG_MONSOON': None,
	'SCATTERBUG_OCEAN': None,
	'SCATTERBUG_POKEBALL': None,
	'SCATTERBUG_POLAR': None,
	'SCATTERBUG_RIVER': None,
	'SCATTERBUG_SANDSTORM': None,
	'SCATTERBUG_SAVANNA': None,
	'SCATTERBUG_SUN': None,
	'SCATTERBUG_TUNDRA': None,
	'SPEWPA_ARCHIPELAGO': None,
	'SPEWPA_CONTINENTAL': None,
	'SPEWPA_ELEGANT': None,
	'SPEWPA_FANCY': None,
	'SPEWPA_GARDEN': None,
	'SPEWPA_HIGH_PLAINS': None,
	'SPEWPA_ICY_SNOW': None,
	'SPEWPA_JUNGLE': None,
	'SPEWPA_MARINE': None,
	'SPEWPA_MEADOW': None,
	'SPEWPA_MODERN': None,
	'SPEWPA_MONSOON': None,
	'SPEWPA_OCEAN': None,
	'SPEWPA_POKEBALL': None,
	'SPEWPA_POLAR': None,
	'SPEWPA_RIVER': None,
	'SPEWPA_SANDSTORM': None,
	'SPEWPA_SAVANNA': None,
	'SPEWPA_SUN': None,
	'SPEWPA_TUNDRA': None,
	'VIVILLON_ARCHIPELAGO': None,
	'VIVILLON_CONTINENTAL': None,
	'VIVILLON_ELEGANT': None,
	'VIVILLON_FANCY': None,
	'VIVILLON_GARDEN': None,
	'VIVILLON_HIGH_PLAINS': None,
	'VIVILLON_ICY_SNOW': None,
	'VIVILLON_JUNGLE': None,
	'VIVILLON_MARINE': None,
	'VIVILLON_MEADOW': None,
	'VIVILLON_MODERN': None,
	'VIVILLON_MONSOON': None,
	'VIVILLON_OCEAN': None,
	'VIVILLON_POKEBALL': None,
	'VIVILLON_POLAR': None,
	'VIVILLON_RIVER': None,
	'VIVILLON_SANDSTORM': None,
	'VIVILLON_SAVANNA': None,
	'VIVILLON_SUN': None,
	'VIVILLON_TUNDRA': None,
	'LITLEO': 2,
	'PYROAR_FEMALE': None,
	'PYROAR_NORMAL': None,
	'FLABEBE_BLUE': 2,
	'FLABEBE_ORANGE': 2,
	'FLABEBE_RED': 2,
	'FLABEBE_WHITE': 2,
	'FLABEBE_YELLOW': 2,
	'FLOETTE_BLUE': None,
	'FLOETTE_ORANGE': None,
	'FLOETTE_RED': None,
	'FLOETTE_WHITE': None,
	'FLOETTE_YELLOW': None,
	'FLORGES_BLUE': None,
	'FLORGES_ORANGE': None,
	'FLORGES_RED': None,
	'FLORGES_WHITE': None,
	'FLORGES_YELLOW': None,
	'SKIDDO': None,
	'GOGOAT': None,
	'PANCHAM': None,
	'PANGORO': None,
	'FURFROU_DANDY': 1,
	'FURFROU_DEBUTANTE': 1,
	'FURFROU_DIAMOND': 1,
	'FURFROU_HEART': 1,
	'FURFROU_KABUKI': 1,
	'FURFROU_LA_REINE': 1,
	'FURFROU_MATRON': 1,
	'FURFROU_NATURAL': 1,
	'FURFROU_PHARAOH': 1,
	'FURFROU_STAR': 1,
	'ESPURR': None,
	'MEOWSTIC_FEMALE': None,
	'MEOWSTIC_NORMAL': None,
	'HONEDGE': None,
	'SPRITZEE': 2,
	'AROMATISSE': None,
	'SWIRLIX': 2,
	'SLURPUFF': None,
	'INKAY': 3,
	'MALAMAR': 3,
	'BINACLE': None,
	'BARBARACLE': None,
	'SKRELP': 2,
	'DRAGALGE': None,
	'CLAUNCHER': 2,
	'CLAWITZER': None,
	'HELIOPTILE': 2,
	'HELIOLISK': None,
	'TYRUNT': 3,
	'TYRANTRUM': None,
	'AMAURA': 3,
	'AURORUS': None,
	'SYLVEON': None,
	'HAWLUCHA': None,
	'DEDENNE': 2,
	'CARBINK': None,
	'GOOMY': 2,
	'SLIGGOO': None,
	'GOODRA': None,
	'KLEFKI': None,
	'PHANTUMP': None,
	'TREVENANT': None,
	'PUMPKABOO_AVERAGE': None,
	'PUMPKABOO_LARGE': None,
	'PUMPKABOO_SMALL': None,
	'PUMPKABOO_SUPER': None,
	'GOURGEIST_AVERAGE': None,
	'GOURGEIST_LARGE': None,
	'GOURGEIST_SMALL': None,
	'GOURGEIST_SUPER': None,
	'BERGMITE': 1,
	'AVALUGG_HISUIAN': None,
	'AVALUGG_NORMAL': None,
	'NOIBAT': 2,
	'NOIVERN': None,
	'XERNEAS': None,
	'YVELTAL': None,
	'ZYGARDE': None,
	'DIANCIE': None,
	'HOOPA_CONFINED': None,
	'HOOPA_UNBOUND': None,
	'VOLCANION': None,
	'ROWLET': 1,
	'DARTRIX': None,
	'DECIDUEYE': None,
	'LITTEN': 1,
	'TORRACAT': 1, #unconfirmed
	'INCINEROAR': 1, #unconfirmed
	'POPPLIO': 1,
	'BRIONNE': None,
	'PRIMARINA': None,
	'PIKIPEK': 2,
	'TRUMBEAK': None,
	'TOUCANNON': None,
	'YUNGOOS': 2,
	'GUMSHOOS': None,
	'GRUBBIN': 2,
	'CHARJABUG': None,
	'VIKAVOLT': None,
	'CRABRAWLER': 2,
	'CRABOMINABLE': None,
	'ORICORIO_BAILE': 2,
	'ORICORIO_PAU': 2,
	'ORICORIO_POMPOM': 2,
	'ORICORIO_SENSU': 2,
	'CUTIEFLY': 2,
	'RIBOMBEE': None,
	'ROCKRUFF': None,
	'LYCANROC_DUSK': None,
	'LYCANROC_MIDDAY': None,
	'LYCANROC_MIDNIGHT': None,
	'WISHIWASHI_SCHOOL': None,
	'WISHIWASHI_SOLO': None,
	'MAREANIE': 2,
	'TOXAPEX': None,
	'MUDBRAY': None,
	'MUDSDALE': None,
	'DEWPIDER': None,
	'ARAQUANID': None,
	'FOMANTIS': 3,
	'LURANTIS': None,
	'MORELULL': 3,
	'SHIINOTIC': None,
	'SALANDIT': None,
	'SALAZZLE': None,
	'STUFFUL': 2,
	'BEWEAR': None,
	'BOUNSWEET': None,
	'STEENEE': 3,
	'TSAREENA': None,
	'COMFEY': None,
	'ORANGURU': None,
	'PASSIMIAN': None,
	'WIMPOD': 2,
	'GOLISOPOD': None,
	'SANDYGAST': None,
	'PALOSSAND': None,
	'PYUKUMUKU': None,
	'TYPE_NULL': None,
	'SILVALLY_BUG': None,
	'SILVALLY_DARK': None,
	'SILVALLY_DRAGON': None,
	'SILVALLY_ELECTRIC': None,
	'SILVALLY_FAIRY': None,
	'SILVALLY_FIGHTING': None,
	'SILVALLY_FIRE': None,
	'SILVALLY_FLYING': None,
	'SILVALLY_GHOST': None,
	'SILVALLY_GRASS': None,
	'SILVALLY_GROUND': None,
	'SILVALLY_ICE': None,
	'SILVALLY_NORMAL': None,
	'SILVALLY_POISON': None,
	'SILVALLY_PSYCHIC': None,
	'SILVALLY_ROCK': None,
	'SILVALLY_STEEL': None,
	'SILVALLY_WATER': None,
	'MINIOR_BLUE': None,
	'MINIOR_GREEN': None,
	'MINIOR_INDIGO': None,
	'MINIOR_ORANGE': None,
	'MINIOR_RED': None,
	'MINIOR_VIOLET': None,
	'MINIOR_YELLOW': None,
	'KOMALA': None,
	'TURTONATOR': None,
	'TOGEDEMARU': 2,
	'MIMIKYU_BUSTED': None,
	'MIMIKYU_DISGUISED': None,
	'BRUXISH': 3,
	'DRAMPA': None,
	'DHELMISE': None,
	'JANGMO_O': 2,
	'HAKAMO_O': None,
	'KOMMO_O': None,
	'TAPU_KOKO': None,
	'TAPU_LELE': None,
	'TAPU_BULU': None,
	'TAPU_FINI': None,
	'COSMOG': None,
	'COSMOEM': None,
	'SOLGALEO': None,
	'LUNALA': None,
	'NIHILEGO': None,
	'BUZZWOLE': None,
	'PHEROMOSA': None,
	'XURKITREE': None,
	'CELESTEELA': None,
	'KARTANA': None,
	'GUZZLORD': None,
	'NECROZMA_DAWN_WINGS': None,
	'NECROZMA_DUSK_MANE': None,
	'NECROZMA_NORMAL': None,
	'NECROZMA_ULTRA': None,
	'MAGEARNA_NORMAL': None,
	'MAGEARNA_ORIGINAL_COLOR': None,
	'MARSHADOW': None,
	'POIPOLE': None,
	'NAGANADEL': None,
	'STAKATAKA': None,
	'BLACEPHALON': None,
	'ZERAORA': None,
	'MELTAN': None,
	'MELMETAL': None,
	'GROOKEY': None,
	'THWACKEY': None,
	'RILLABOOM': None,
	'SCORBUNNY': None,
	'RABOOT': None,
	'CINDERACE': None,
	'SOBBLE': None,
	'DRIZZILE': None,
	'INTELEON': None,
	'SKWOVET': None,
	'GREEDENT': None,
	'ROOKIDEE': None,
	'CORVISQUIRE': None,
	'CORVIKNIGHT': None,
	'BLIPBUG': None,
	'DOTTLER': None,
	'ORBEETLE': None,
	'NICKIT': None,
	'THIEVUL': None,
	'GOSSIFLEUR': None,
	'ELDEGOSS': None,
	'WOOLOO': None,
	'DUBWOOL': None,
	'CHEWTLE': None,
	'DREDNAW': None,
	'YAMPER': None,
	'BOLTUND': None,
	'ROLYCOLY': None,
	'CARKOL': None,
	'COALOSSAL': None,
	'APPLIN': None,
	'FLAPPLE': None,
	'APPLETUN': None,
	'SILICOBRA': None,
	'SANDACONDA': None,
	'CRAMORANT': None,
	'ARROKUDA': None,
	'BARRASKEWDA': None,
	'TOXEL': None,
	'TOXTRICITY_AMPED': None,
	'TOXTRICITY_LOW_KEY': None,
	'SIZZLIPEDE': None,
	'CENTISKORCH': None,
	'CLOBBOPUS': None,
	'GRAPPLOCT': None,
	'SINISTEA_ANTIQUE': None,
	'SINISTEA_PHONY': None,
	'POLTEAGEIST_ANTIQUE': None,
	'POLTEAGEIST_PHONY': None,
	'HATENNA': None,
	'HATTREM': None,
	'HATTERENE': None,
	'IMPIDIMP': None,
	'MORGREM': None,
	'GRIMMSNARL': None,
	'OBSTAGOON_NORMAL': None,
	'PERRSERKER_NORMAL': None,
	'CURSOLA_NORMAL': None,
	'SIRFETCHD_NORMAL': None,
	'MR_RIME_NORMAL': None,
	'RUNERIGUS_NORMAL': None,
	'MILCERY': None,
	'ALCREMIE': None,
	'FALINKS': None,
	'PINCURCHIN': None,
	'SNOM': None,
	'FROSMOTH': None,
	'STONJOURNER': None,
	'EISCUE_ICE': None,
	'EISCUE_NOICE': None,
	'INDEEDEE_FEMALE': None,
	'INDEEDEE_MALE': None,
	'MORPEKO_FULL_BELLY': None,
	'MORPEKO_HANGRY': None,
	'CUFANT': None,
	'COPPERAJAH': None,
	'DRACOZOLT': None,
	'ARCTOZOLT': None,
	'DRACOVISH': None,
	'ARCTOVISH': None,
	'DURALUDON': None,
	'DREEPY': None,
	'DRAKLOAK': None,
	'DRAGAPULT': None,
	'ZACIAN_CROWNED_SWORD': None,
	'ZACIAN_HERO': None,
	'ZAMAZENTA_CROWNED_SHIELD': None,
	'ZAMAZENTA_HERO': None,
	'ETERNATUS_ETERNAMAX': None,
	'ETERNATUS_NORMAL': None,
	'KUBFU': None,
	'URSHIFU_RAPID_STRIKE': None,
	'URSHIFU_SINGLE_STRIKE': None,
	'ZARUDE': None,
	'REGIELEKI': None,
	'REGIDRAGO': None,
	'GLASTRIER': None,
	'SPECTRIER': None,
	'CALYREX_ICE_RIDER': None,
	'CALYREX_NORMAL': None,
	'CALYREX_SHADOW_RIDER': None,
	'URSALUNA': None,
	'SNEASLER': None,
	'OVERQWIL': None,
	'GIMMIGHOUL': None,
	'GHOLDENGO': None,
	'UNOWN': None,
	'SPINDA': None
}
