
// human NPCs we interact with

/*
classes

  MercahtWeapons

  MerchantArmor

  MerchantMagic

  MerchantRations

  Guard

  Jester

  


*/

export class NPC
{
  constructor( npcclass, position )
  {
    this.class = npcclass;
    this.position = position;
    this.weapon = undefined;
    this.strength = undefined;
  }

  update()
  {
  }

  draw()
  {
  }
}