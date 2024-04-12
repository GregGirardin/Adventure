import { c } from './constants.js';
import { Point } from './utils.js'

export class Party
{
  constructor( )
  {
    let members = []; // Characters
    this.weapons = []; // the party inventory that can be passed around
    this.armor = [];
    this.gold = 0;
  }
}

export class Character
{
  constructor( name, position )
  {
    this.position = position;
    this.name = name;
    this.class = undefined;
    this.level = 1;

    this.intelligence = 10;
    this.strength = 10;
    this.dexterity = 10;
    this.magic = 0;

    this.hitpoints = 10;

    this.weapons = undefined;
    this.armor = undefined;

    this.tid = 0; // which tileId
  }

  update()
  {
  }

  draw()
  {
  }

}


export class Weapon 
{
  constructor()
  {
    this.type = undefined; 
    this.range = 1;
    this.damage = 0;
    this.count = 0;
    this.weight = 0;
    this.price = 0;

  }
}

export class armor
{
  constructor()
  {
    this.name = 0;
    this.weight = 0;
    this.protecton = 0
    this.price = 0;
    this.spriteId = 0;

  }
}